---
name: maintain-atomic-commits
description: Fold a change into the local commit it belongs to instead of adding a follow-up. Use for amendments, earlier-commit corrections, rewording, and changes that map to one or more existing local commits; not for a new commit or ordinary rebasing.
---

# maintain-atomic-commits

Read [conventions](references/conventions.md). First establish the target is
local and rewriteable: `git log --oneline <base>..HEAD`. Never rewrite a commit
reachable from a shared branch.

| Change | Action |
| --- | --- |
| Belongs in `HEAD` | Stage it, then `git commit --amend` (`--no-edit` if appropriate). |
| Belongs in an older commit and must be authored in that state | `git rebase -i <base>`, mark it `edit`, amend, then `git rebase --continue`. |
| Already-made changes map to one or more older commits | Stage each target's hunks, `git commit --fixup <commit>`, then `git rebase -i --autosquash <base>`. |

Prefer the first applicable route. Use `git add -p` when one file supplies
hunks to several targets. Before autosquashing, show the resulting fixups and
their target mapping. If replay conflicts, use `resolve-merge-conflict` and
continue; replaying later commits is expected to surface conflicts.
