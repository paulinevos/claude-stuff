# Jujutsu conventions for parallel slices

Shared context for the jj-workflow skills. Read it when splitting work into
slices, shaping revisions, or touching another agent's workspace. Keywords
(MUST, MUST NOT, SHOULD) are normative. Verified against jj 0.43.

## Vocabulary

- A **slice** is one independently reviewable unit of work: one bookmark, one
  pull request, one or more revisions.
- A **workspace** is a jj working copy attached to the shared repository. There
  is one per slice, named after the slice. The original checkout is the
  `default` workspace and belongs to the orchestrator.
- A slice's **base** is the revset it builds on: `trunk()` (the default remote
  bookmark, usually `main@origin`) for an independent slice, or the parent
  slice's bookmark for a dependent one.

## One owner per workspace, bookmark and change

- Every workspace, every slice bookmark, and every change ID under a slice
  bookmark has exactly one owner at a time: the worker in that workspace. You
  MUST NOT describe, squash, rebase, abandon, or move bookmarks that belong to
  another slice.
- Nobody MAY rewrite a revision that another workspace's `@` descends from while
  that worker is active. Doing so makes the other workspace **stale**; if it
  also held unsnapshotted edits, recovery produces a **divergent** change and
  the edits leave the working copy. A parent slice MAY still *add* revisions at
  its tip while a dependent slice is active; only rewriting existing ones is a
  problem.
- Read other workspaces through revsets from your own workspace, never by
  running jj inside theirs: `jj log -r '<slice>@'`, `jj log -r 'trunk()..<slice>'`.
  Every jj command snapshots the working copy of the workspace it runs against,
  so a plain `jj -R <other-workspace>` captures that worker's half-written files
  into their `@`. If you must use `-R`, add `--ignore-working-copy`.

## Layout and naming

- Workspaces MUST live outside every working copy, in a sibling directory:
  `../<repo>.workspaces/<slice>`. A workspace created inside the main working
  copy is snapshotted as ordinary files.
- Create the parent directory first; `jj workspace add` does not create it.
- Workspace name, bookmark name and slice name MUST be identical, in
  lowercase-kebab-case (`api-client`, `api-client-tests`).

## Granular revisions

- Each revision MUST be one logical step that builds and passes tests on its
  own, so reviewers can read the bookmark revision by revision.
- Descriptions follow the usual commit-message rules: imperative, capitalised
  subject without a trailing period; blank line; body wrapped at 72 columns
  saying *why*.
- Every revision under a bookmark MUST have a description before hand-off.
  `jj git push` refuses commits without one.
- Fixes MUST be folded into the revision they belong to (`jj squash --into
  <rev>`, or `jj absorb`), never stacked as "Fix typo" revisions. Descendants
  and bookmarks follow the rewrite automatically.
- `@` is scratch space. At rest it MUST be empty and undescribed, sitting on
  top of the slice's newest revision; the bookmark points at `@-`.

## Bookmarks

- One bookmark per slice, on the slice's newest described revision. Bookmarks
  follow rewrites of their target but do NOT advance when you `jj new` on top;
  move them yourself with `jj bookmark move <slice> --to @-`.
- A bookmark MUST NOT point at an empty, undescribed change: it would be pushed
  as-is and it keeps that change alive when the workspace is forgotten.
- Base bookmarks (`trunk()`, tags, untracked remote bookmarks) are immutable.
  You MUST NOT use `--ignore-immutable`.

## Staying current

- Rebase, don't merge: `jj git fetch && jj rebase -b <slice> -o <base>`.
- Conflicts never block a jj command; they are recorded inside the affected
  revisions (`conflicts()` revset, `(conflict)` in the log). They MUST be
  resolved before hand-off and MUST NOT be pushed.

## Driving jj from a script or an agent

- Add `--no-pager --color never` to every command; add `--quiet` when only the
  primary output matters.
- List revisions with `jj log --no-graph -T '<template>'` rather than parsing
  the graph, e.g. `-T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'`.
- Use `--ignore-working-copy` for read-only inspection so the command neither
  snapshots nor updates the working copy.
- Refer to revisions by change ID, not commit ID: change IDs survive rewrites.

## When jj is the wrong tool

- `jj root` fails: the repository is not a jj repo. Use the git fallback.
- `.gitmodules` exists and the work or its build/tests need submodule content:
  use the git fallback. jj does not materialise submodules in a workspace
  (the directory is simply absent), so nothing that depends on them can run.
- Not colocated (`jj git colocation status` says so): git-based tools such as
  `gh` need `GIT_DIR=$(jj git root)`.
