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

Shared conventions — atomic-commit rules, commit-message style, stashing to
clear the tree, and preferring rebase over pull+merge — live in
`skills/maintain-atomic-commits/references/conventions.md`, bundled with that
skill so they travel on install (including to non-Claude agents). The other
skills inline the one or two rules they need, so each is self-contained.

All rewrite operations respect one rule: never rewrite commits that already
exist on a public branch (`main`, `develop`, …). See the bundled conventions
above.

## Install

### Via `npx skills` (any supported agent)

Install all skills, or pick individual ones:

```sh
npx skills add paulinevos/claude-stuff              # all four skills
npx skills add paulinevos/claude-stuff --list       # preview without installing
npx skills add paulinevos/claude-stuff -s bisect-debug   # a single skill
```

### Via Claude Code `/plugin`

Add the marketplace, then install the plugin:

```
/plugin marketplace add paulinevos/claude-stuff
/plugin install git-workflow@vos
```
