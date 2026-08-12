---
name: finish-slices
description: "Publish and clean up after parallel slices in Jujutsu (jj) workspaces: verify each slice's revisions from the default workspace, push bookmarks parents-first only after explicit approval, forget the workspaces and delete their directories, and remove bookmarks once their pull requests merge. Use when workers have handed off, when asked to \"push the slices\", \"open PRs for the bookmarks\", \"clean up the jj workspaces\", \"forget the workspace\", \"the PR merged, tidy up\", or when jj workspace list shows leftovers from earlier runs. Not for planning (parallel-slices), work inside a slice (work-in-slice), or stale and divergent workspaces (sync-workspace)."
---

# finish-slices

Run everything here from the default workspace (the original checkout). Verify,
publish with consent, then remove what is no longer needed.

## Steps

1. Verify every slice.

   ```sh
   jj log -r '<base>..<slice>' --no-graph --reversed -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
   jj log -r '(<base>..<slice>) & (conflicts() | description(exact:""))'   # must print nothing
   jj log -r '(<slice>:: ~ <slice>) ~ working_copies() ~ ::(bookmarks() ~ <slice>)'   # must print nothing
   ```

   The third line catches revisions the worker forgot to move the bookmark
   onto (revisions belonging to a child slice are excluded). If anything prints, send the slice back to its worker, or
   fix it yourself only if the worker is finished and the fix is mechanical
   (`jj bookmark move <slice> --to <change-id>`).

2. Bring slices up to date if the base moved since hand-off:
   `jj git fetch && jj rebase -b <slice> -o trunk()`; dependent slices
   `jj rebase -b <child> -o <parent-slice>`. Workers are done, so making their
   workspaces stale is fine. Re-run step 1.

3. Publish, with approval. Show the user the per-slice lists from step 1 and the
   push order, and wait for an explicit yes. Then, parents before children:

   ```sh
   jj git push --bookmark <slice>
   ```

   New bookmarks are tracked automatically; a later push after a rebase is a
   force-with-lease, so it is safe to repeat. For a stacked pull request, set
   its base branch to the parent slice's branch. When the parent merges:
   `jj git fetch && jj rebase -b <child> -o trunk()`, push again, and retarget
   the PR to `main`.

4. Forget the workspaces and delete their directories:

   ```sh
   jj workspace forget <slice-a> <slice-b>
   rm -rf ../<repo>.workspaces/<slice-a> ../<repo>.workspaces/<slice-b>
   jj workspace list
   ```

   Forget by name from the default workspace: forgetting the workspace you are
   standing in leaves you in a directory without a working copy. An empty
   undescribed `@` is abandoned automatically. A non-empty `@` stays behind as
   an anonymous head: squash it into the slice if it is finished work, or
   `jj abandon <change-id>` if not. Bookmarks survive forgetting.

5. After the pull requests merge:

   ```sh
   jj git fetch
   jj bookmark list
   jj bookmark delete <slice>                 # if the local bookmark is still there
   jj log -r 'heads(mutable()) ~ working_copies()'   # anonymous leftovers, usually none
   ```

   `delete` also removes the remote branch on the next push; use
   `jj bookmark forget <slice>` instead if the forge already deleted it and
   you only want the local name gone.

## Why cleanup is a separate step

A forgotten workspace is just a directory; jj never deletes files for you, and
it never removes a bookmark on its own. Leaving them around costs disk and,
worse, invites the next run to reuse a stale workspace and inherit its `@`.
Doing verification, publishing and removal in one pass keeps the repository in
the same state the orchestrator found it in, plus the pushed bookmarks.
