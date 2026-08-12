---
name: parallel-slices
description: "Coordinate several agents working in parallel on one repository with Jujutsu (jj) workspaces, as the orchestrator: detect whether this is a jj repo (and whether git submodules rule jj out), split the task into slices with explicit dependencies, create one workspace per slice in a sibling directory, dispatch a worker per slice with its bookmark name and base, monitor without interfering, and integrate at the end. Use when asked to parallelise implementation, fan out subagents or workers over a codebase, \"use jj workspaces\", \"one PR per slice\", \"stack these changes\", or when planning multi-agent work in a repo that has a .jj directory. Falls back to git worktrees when jj is not usable. Not for doing the work inside a slice (work-in-slice), repairing a stale or divergent workspace (sync-workspace), or pushing and cleaning up (finish-slices)."
---

# parallel-slices

You are the orchestrator. Decide whether jj is the right tool, cut the task into
slices, give every slice its own workspace, and keep your hands off those
workspaces until the workers hand off. Shared rules live in
[conventions](references/conventions.md); the git variant in
[git-fallback](references/git-fallback.md).

## Step 1: detect the version control system

```sh
jj root                          # prints the workspace root if this is a jj repo
git rev-parse --show-toplevel    # only if jj root fails
test -f "$(jj root)/.gitmodules" && echo "has submodules"
jj git colocation status         # tells you whether git tools work here too
```

| Situation | Do |
| --- | --- |
| `jj root` fails, git succeeds | Follow [git-fallback](references/git-fallback.md) and say so |
| jj repo, no `.gitmodules` | Continue with jj |
| jj repo, `.gitmodules` present, and the work or its build/tests need submodule content | Follow the git fallback; explain that jj workspaces do not materialise submodules (the directory is absent) |
| jj repo, `.gitmodules` present, submodules irrelevant to this task | Continue with jj; note that nothing depending on the submodules can run in the workspaces |
| Neither jj nor git | Stop and tell the user |

## Step 2: slice the work

A slice is one reviewable pull request: a coherent purpose, its own set of
files, testable on its own. For each slice record its name
(lowercase-kebab), its base, the files it will touch, and what "done" means.

- Slice B **depends on** slice A when B needs code A introduces. Base B on A's
  bookmark; base independent slices on `trunk()`.
- Two slices editing the same files is a smell: merge them, or make one depend
  on the other. Fewer, well-separated slices beat many overlapping ones.
- Show the user the slice table before creating anything.

## Step 3: create a workspace per slice

```sh
jj git fetch
repo=$(basename "$(jj root)")
mkdir -p "../$repo.workspaces"                       # jj does not create parent directories
jj workspace add --name <slice> -r 'trunk()' --sparse-patterns full "../$repo.workspaces/<slice>"
jj workspace list
```

Each workspace starts with an empty `@` on top of its base. Do **not** create
the slice bookmark yourself: a bookmark on an empty, undescribed change is
pushed as-is and keeps that change alive at cleanup. The worker creates it on
their first described revision.

Dependent slices: create the workspace with `-r <parent-slice>` once the
parent's bookmark exists. Prefer to start a dependent slice after its parent
hands off. If it must start earlier, tell both workers: the parent MAY add
revisions at its tip but MUST NOT rewrite existing ones (squash, describe,
rebase) until the child hands off, because that rewrites the child's ancestors
and makes the child's workspace stale.

## Step 4: dispatch workers

Give every worker, verbatim:

- the workspace path and the instruction to work only inside it;
- the slice name (also the bookmark name) and its base revset (`trunk()` or
  `<parent-slice>`);
- the purpose, the files it owns, and the hand-off criteria;
- the instruction to follow the `work-in-slice` skill and to never touch
  revisions or bookmarks of other slices.

## Step 5: monitor without interfering

From your own (default) workspace only:

```sh
jj workspace list
jj log -r 'trunk()..(<slice>@ | <slice>)' --no-graph -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
jj log -r 'conflicts() & mutable()'
```

Every jj command snapshots the working copy of the workspace it runs against,
so never run a plain `jj -R <worker-workspace>`: it would commit that worker's
half-written files into their `@`. Revsets like `<slice>@` see everything you
need from here; if you must use `-R`, add `--ignore-working-copy`.

## Step 6: integrate

When all workers have handed off, switch to `finish-slices`. If a dependent
slice needs re-parenting because its parent grew, do it now from the default
workspace: `jj rebase -b <child> -o <parent-slice>`. The child workspace becomes
stale, which no longer matters after hand-off.

## Why workspaces rather than clones or git worktrees

All workspaces share one repository: a revision or bookmark created in one is
visible in every other immediately, with no push or pull between agents. jj's
operation log is lock-free, so concurrent commands from different workspaces
merge instead of failing. The price is the ownership rule above: the only way
two agents interfere is by rewriting each other's revisions, which is why each
change ID and bookmark has exactly one owner.
