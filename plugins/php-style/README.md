# php-style

Claude Code plugin with one skill: PHP code conventions centred on **object
calisthenics**.

| Skill | Use when |
| --- | --- |
| `php-object-calisthenics` | Writing, refactoring or reviewing PHP — including small edits, bug fixes, tests and scripts |

The skill covers the eight calisthenics rules (one level of indentation per
method, no `else`, wrapped primitives, first-class collections, one dot per
line, no abbreviations, small entities, no getters or setters) together with the
PHP specifics that make them cheap: `declare(strict_types=1)`, readonly value
objects with named constructors, backed enums carrying behaviour, `match` over
`switch`, `final` by default, constructor property promotion, and
domain-specific exceptions. Laravel projects with Boost installed defer to
Boost's version-specific guidelines.

It's a single self-contained `SKILL.md` with no references, so it travels intact
on install (including to non-Claude agents). Repository conventions always win
over the skill; the skill says so.

## Install

### Via `npx skills` (any supported agent)

```sh
npx skills add paulinevos/claude-stuff                        # all skills
npx skills add paulinevos/claude-stuff --list                 # preview without installing
npx skills add paulinevos/claude-stuff -s php-object-calisthenics   # just this one
```

### Via Claude Code `/plugin`

Add the marketplace, then install the plugin:

```
/plugin marketplace add paulinevos/claude-stuff
/plugin install php-style@vos
```
