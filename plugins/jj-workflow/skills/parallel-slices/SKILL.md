---
name: parallel-slices
description: "Coordinate parallel work in Jujutsu workspaces: choose jj or a git-worktree fallback, split reviewable slices, create and dispatch isolated workspaces, monitor safely, and integrate. Use when planning or orchestrating multi-agent work in a jj repository."
---

# parallel-slices

You orchestrate; workers own their workspaces. Read
[conventions](references/conventions.md). Use [git-fallback](references/git-fallback.md)
if `jj root` fails, or if required work/tests need git submodules. A jj repo
with irrelevant submodules may continue, but the workspaces cannot materialise
them. Stop if neither jj nor git applies.

1. Split work into independently testable, reviewable slices. Record name,
   base, owned files, and done criteria; show the table before creating
   anything. Independent slices base on `trunk()`; dependent slices base on the
   parent's bookmark. Avoid overlapping files.
2. Create each workspace outside checkouts, always at
   `${HOME}/.jj-workspaces/<repo>/<slice>`:

   ```sh
   jj git fetch
   repo=$(basename "$(jj root)")
   workspace_root="${HOME}/.jj-workspaces/${repo}"
   mkdir -p "$workspace_root"
   jj workspace add --name <slice> -r 'trunk()' --sparse-patterns full "$workspace_root/<slice>"
   ```

   For a dependent slice, use `-r <parent-slice>` only after that bookmark
   exists. Do not create a bookmark on its initial empty `@`.
3. Give each worker its workspace path, slice/bookmark and base, purpose,
   owned files, hand-off criteria, and `work-in-slice`. They must not touch
   other slices. If a child starts before hand-off, its parent may add at the
   tip but must not rewrite ancestors.
4. Monitor from the default workspace with revsets, not commands in worker
   directories. A plain `jj -R <workspace>` snapshots that worker's edits; if
   `-R` is unavoidable, add `--ignore-working-copy`.
5. After hand-off, use `finish-slices`. Rebase a child onto a grown parent only
   from the default workspace; its now-stale handed-off workspace is harmless.

All workspaces share revisions and bookmarks immediately. One owner per change,
bookmark, and workspace prevents concurrent rewrites from making workers stale.
