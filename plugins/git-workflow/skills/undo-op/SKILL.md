---
name: undo-op
description: Recover a branch to its state before a local merge, rebase, reset, amend, squash, or other history operation using the reflog; distinct from making a reverting commit.
---

# undo-op

1. Inspect `git reflog` (or `git reflog show <branch>`), find the requested
   operation, and inspect the entry immediately before it with `git log` or
   `git show HEAD@{N}`.
2. Show that target to the user and confirm it is the desired state.
3. If uncommitted work exists, stash it (`git stash -u`); never create a
   checkpoint commit merely to clear the tree.
4. Restore the affected branch with `git reset --hard HEAD@{N}`, then
   `git stash pop` if needed.

Use `git revert` instead when undoing a published commit by adding a new inverse
commit. Reflog recovery rewinds local history; `reset --hard` discards unstashed
changes.
