---
name: resolve-merge-conflict
description: Resolve merge conflicts and continue the interrupted rebase, merge, or cherry-pick. Use whenever git reports conflicts or halts mid-operation with "CONFLICT", "Unmerged paths", "fix conflicts and then commit", or the user asks to resolve/handle conflicts or says an operation is "stuck on a conflict".
---

# resolve-merge-conflict

Reconcile conflicting changes, then resume whatever operation git paused.

## Steps

1. See what's conflicted: `git status` (unmerged paths) and open each file to
   read the `<<<<<<<` / `=======` / `>>>>>>>` markers.
2. Decide the resolution per file:
   - **Consolidate** (the usual case): edit the file so it combines both sides
     coherently, removing the markers. Always show the user your proposed
     resolution and get confirmation before staging — a merge decision is easy
     to get subtly wrong, and it's their code.
   - **Keep the current-branch version wholesale:**
     `git checkout --ours [file]` then `git add [file]`.
   - **Keep the incoming version wholesale:**
     `git checkout --theirs [file]` then `git add [file]`.
3. Stage each resolved file with `git add [file]`.
4. Continue the paused operation: `git rebase --continue`,
   `git cherry-pick --continue`, or `git merge --continue` — match whatever was
   running when the conflict appeared.

## A note on ours/theirs

Their meaning flips depending on the operation: during a rebase, "ours" is the
branch you're rebasing *onto* and "theirs" is your replayed commit — the
opposite of what people expect. When in doubt, inspect the actual content rather
than trusting the labels, and confirm with the user.
