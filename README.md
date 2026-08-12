## Pauline's Claude stuff

This is my mono-repo for assorted Claude stuff. Feel free to use.

## Plugins

Installable via the `vos` marketplace (see `.claude-plugin/marketplace.json`).

### git-workflow

Atomic-commit Git workflow skills, plus shared conventions.

| Skill | Use when |
| --- | --- |
| [`maintain-atomic-commits`](plugins/git-workflow/skills/maintain-atomic-commits/SKILL.md) | A change belongs in an existing commit — routes to amend / edit-in-place / fixup |
| [`resolve-merge-conflict`](plugins/git-workflow/skills/resolve-merge-conflict/SKILL.md) | A merge conflict arises |
| [`undo-op`](plugins/git-workflow/skills/undo-op/SKILL.md) | Undoing a merge, rebase, reset, or amend via the reflog |
| [`bisect-debug`](plugins/git-workflow/skills/bisect-debug/SKILL.md) | Finding and fixing the commit that caused a regression |

Shared conventions (atomic-commit rules, commit-message style, stashing,
rebase-over-merge) live in
`plugins/git-workflow/skills/maintain-atomic-commits/references/conventions.md`,
bundled with that skill so they travel on install to any agent.

### php-style

PHP code conventions centred on object calisthenics.

| Skill | Use when |
| --- | --- |
| [`php-object-calisthenics`](plugins/php-style/skills/php-object-calisthenics/SKILL.md) | Writing, refactoring or reviewing PHP — small edits, bug fixes, tests and scripts included |

**Install** — via `npx skills` (any supported agent):

```sh
npx skills add paulinevos/claude-stuff        # all skills
npx skills add paulinevos/claude-stuff --list # preview without installing
```

or via Claude Code `/plugin`:

```
/plugin marketplace add paulinevos/claude-stuff
/plugin install git-workflow@vos
```
