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

### jj-workflow

Jujutsu (jj) skills for several agents working in parallel on one repository:
a workspace and a bookmark per slice, granular revisions, stacked dependent
slices, stale-workspace recovery, and cleanup. Falls back to git worktrees when
jj is not usable (no `.jj`, or submodules matter).

| Skill | Use when |
| --- | --- |
| [`parallel-slices`](plugins/jj-workflow/skills/parallel-slices/SKILL.md) | Orchestrating: detect jj, slice the task, create a workspace per slice, dispatch and monitor workers |
| [`work-in-slice`](plugins/jj-workflow/skills/work-in-slice/SKILL.md) | Working inside an assigned workspace: described revisions, bookmark on the tip, fold fixes in, hand off |
| [`sync-workspace`](plugins/jj-workflow/skills/sync-workspace/SKILL.md) | "The working copy is stale", a moved base or parent slice, a divergent change, or a `??` bookmark |
| [`finish-slices`](plugins/jj-workflow/skills/finish-slices/SKILL.md) | Verifying, pushing after approval, forgetting workspaces and deleting bookmarks |

Shared conventions and the git-worktree fallback live in
`plugins/jj-workflow/skills/parallel-slices/references/`, bundled with that
skill so they travel on install. Workspaces go in `../<repo>.workspaces/<slice>`,
never inside a working copy.
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
