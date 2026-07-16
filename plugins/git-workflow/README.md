# git-workflow

Claude Code plugin with Git skills for an **atomic-commit** workflow. Each skill
lives in its own directory under `skills/` and loads on demand.

| Skill | Use when |
| --- | --- |
| `maintain-atomic-commits` | A change belongs in an existing commit — routes to amend / edit-in-place / fixup |
| `resolve-merge-conflict` | A merge conflict arises |
| `undo-op` | Undoing a merge, rebase, reset, or amend via the reflog |
| `bisect-debug` | Finding and fixing the commit that caused a regression |

`maintain-atomic-commits` is the core of the workflow: it decides *how* to absorb a
change by *where* it goes and *when* you make it — latest commit → `git commit
--amend`; older commit, change not yet written → interactive-rebase `edit`;
changes already made (possibly across several commits) → `git commit --fixup` +
autosquash.

Shared context lives in `references/conventions.md` — atomic-commit rules,
commit-message style, stashing to clear the tree, and preferring rebase over
pull+merge. The skills link to it.

All rewrite operations respect one rule: never rewrite commits that already
exist on a public branch (`main`, `develop`, …). See `references/conventions.md`.

## Install

Add this repo as a marketplace, then install the plugin:

```
/plugin marketplace add <this-repo>
/plugin install git-workflow@vos
```
