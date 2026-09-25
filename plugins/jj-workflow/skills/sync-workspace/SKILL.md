---
name: sync-workspace
description: Recover a stale, divergent, or conflicted Jujutsu workspace, or rebase a slice onto a moved base or parent. Use for stale-working-copy errors, divergent change IDs, or conflicted bookmarks.
---

# sync-workspace

Identify the symptom before acting.

| Symptom | Recovery |
| --- | --- |
| Stale working copy | `jj workspace update-stale`, then `jj status`. If `@` is divergent and edits disappeared, handle it below. |
| Base or parent moved | `jj git fetch && jj rebase -b <slice> -o <base>`; check `jj log -r 'conflicts() & (<base>..@)'`. Rebase only your slice. |
| Divergent `change/0`, `change/1` | Inspect versions; combine with `jj squash --from <other-commit-id> --into @`, abandon the unwanted version, or preserve both with `jj metaedit --update-change-id <commit-id>`. Verify `jj log -r @` and `jj status`. |
| Bookmark `name??` | Inspect `jj bookmark list <name>`, rebase wanted work together if necessary, then `jj bookmark move <name> --to <change-id>`; fetch for a remote conflict. |

`update-stale` snapshots first. Unsnapshotted edits during an ancestor rewrite
become a divergent change and leave the working copy. jj merges racing
operations rather than locking; one owner per workspace, bookmark, and change
prevents these states.
