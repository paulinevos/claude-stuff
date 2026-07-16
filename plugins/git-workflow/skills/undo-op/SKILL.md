---
name: undo-op
description: Recover the branch to its state before a git operation using the reflog. Use when the user wants to undo or reverse a merge, rebase, reset, amend, squash, or "bad" history rewrite, says "get my commits back", "I messed up the rebase", "revert to before I ran X", or fears they lost commits. This recovers via reflog, distinct from git revert (which makes a new inverse commit).
---

# undo-op

Almost every history-changing operation is reversible because git records where
each ref pointed before it moved, in the reflog. Undoing means finding the entry
just before the operation and moving the branch back to it.

## Steps

1. Inspect recent moves: `git reflog` (or `git reflog show [branch]`). Each line
   shows a `HEAD@{N}` position and the operation that produced it (`rebase`,
   `commit --amend`, `reset`, `merge`, …).
2. Identify the entry that describes the operation the user wants to undo, then
   look one entry *older* — that's the state to return to. Confirm by inspecting
   it: `git log --oneline HEAD@{N}` and/or `git show HEAD@{N}`.
3. Show the user that state and confirm it's the outcome they expect **before**
   changing anything — the next step is destructive to the current tip.
4. Restore: `git reset --hard HEAD@{N}` (run on the affected branch). The branch
   now points where it did before the operation.

## Why the reflog, not `git revert`

`git revert` adds a new commit that inverts a change — appropriate for undoing a
*published* commit. Here the goal is to rewind local history as if the operation
never happened, which `reset --hard` to a reflog position does cleanly. Because
reflog entries persist for a while, even a "lost" commit after a bad rebase is
usually still recoverable this way.

Caution: `reset --hard` discards uncommitted changes. If there are any, stash
them first with `git stash` (`-u` to include untracked files), then
`git stash pop` after the reset.
