## Pauline's Claude stuff

This is my mono-repo for assorted Claude stuff. Feel free to use.

## Plugins

Installable via the `vos` marketplace (see `.claude-plugin/marketplace.json`).

### git-workflow

Atomic-commit Git workflow skills, plus shared conventions.

| Skill | Use when |
| --- | --- |
| `maintain-atomic-commits` | A change belongs in an existing commit — routes to amend / edit-in-place / fixup |
| `resolve-merge-conflict` | A merge conflict arises |
| `undo-op` | Undoing a merge, rebase, reset, or amend via the reflog |
| `bisect-debug` | Finding and fixing the commit that caused a regression |

Shared context lives in `plugins/git-workflow/references/conventions.md`
(atomic-commit rules, commit-message style, stashing, rebase-over-merge).
