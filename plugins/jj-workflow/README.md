# jj-workflow

Claude Code plugin with Jujutsu (jj) skills for **several agents working in
parallel on one repository**. One jj workspace and one bookmark per slice of
work, granular revisions so each PR reads step by step, dependent slices
stacked on their parent, and a clean hand-off/cleanup protocol. Each skill
lives in its own directory under `skills/` and loads on demand.

| Skill | Use when |
| --- | --- |
| `parallel-slices` | Planning parallel work: detect jj (or fall back to git worktrees), split into slices with dependencies, create a workspace per slice, dispatch and monitor workers |
| `work-in-slice` | You are a worker with a workspace path and a slice name: build described revisions, keep the bookmark on the tip, fold fixes in, hand off |
| `sync-workspace` | "The working copy is stale", a base or parent slice moved, a `(divergent)` change, or a `??` bookmark |
| `finish-slices` | Verifying, pushing (after approval), then after a PR merges forgetting its workspace, deleting its directory and bookmark |

`parallel-slices` is the orchestrator's entry point: it decides jj versus git,
slices the task, and hands each worker a workspace. Workers follow
`work-in-slice` and never touch another slice's revisions or bookmarks; that
one rule is what keeps workspaces from going stale or diverging while people
are inside them.

Shared conventions (ownership, layout, granular revisions, bookmark rules,
machine-readable flags, when jj is the wrong tool) live in
`skills/parallel-slices/references/conventions.md`, next to the git-worktree
fallback in `references/git-fallback.md`. Both are bundled with that skill so
they travel on install (including to non-Claude agents). The other skills
inline the one or two rules they need, so each is self-contained.

Workspaces are created under `${HOME}/.jj-workspaces/<repo>/<slice>`, never
inside a working copy. This centralises all workspace edit permissions. Once a
slice's PR merges, its workspace is forgotten with `jj workspace forget` and
its directory is removed. Requires jj 0.43 or later on `PATH`; verified
against 0.43.

## Install

### Via `npx skills` (any supported agent)

Install all skills, or pick individual ones:

```sh
npx skills add paulinevos/claude-stuff                    # every skill in the repo
npx skills add paulinevos/claude-stuff --list             # preview without installing
npx skills add paulinevos/claude-stuff -s work-in-slice   # a single skill
```

### Via Claude Code `/plugin`

Add the marketplace, then install the plugin:

```
/plugin marketplace add paulinevos/claude-stuff
/plugin install jj-workflow@vos
```
