---
name: resolve-merge-conflict
description: Resolve conflicts and continue an interrupted git rebase, merge, or cherry-pick. Use for unmerged paths, conflict markers, or a paused history operation.
---

# resolve-merge-conflict

1. Run `git status`; inspect every file with conflict markers.
2. Decide per file: normally combine both changes coherently. Show that
   resolution to the user and get confirmation before staging. To take a whole
   side, use `git checkout --ours <file>` or `git checkout --theirs <file>`.
3. Remove markers, `git add` each resolved file, and continue the operation:
   `git rebase --continue`, `git merge --continue`, or
   `git cherry-pick --continue`.

During a rebase, `ours` is the branch being rebased *onto* and `theirs` is the
replayed commit. Inspect content rather than relying on those labels.
