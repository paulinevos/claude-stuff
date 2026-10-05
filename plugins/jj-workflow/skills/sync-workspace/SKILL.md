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
| Divergence you cannot rewrite | The versions are immutable. See below. |

`update-stale` snapshots first. Unsnapshotted edits during an ancestor rewrite
become a divergent change and leave the working copy. jj merges racing
operations rather than locking; one owner per workspace, bookmark, and change
prevents these states.

## Divergence in immutable history

`jj squash` and `jj abandon` need mutable revisions, so neither applies once
the divergent versions are published. Never reach for `--ignore-immutable`;
diagnose instead, because the cause decides the fix:

```sh
jj log -r 'divergent()' --no-graph -T 'commit_id.short() ++ " imm=" ++ if(immutable,"Y","n") ++ " [" ++ bookmarks ++ "]\n"'
jj diff --from <one-commit-id> --to <other-commit-id> --stat   # empty = duplicates
jj log -r '<bookmark> ~ ::main'                                # empty = nothing unique
```

Both empty means a stale bookmark — typically a merged pull request whose
branch the forge kept, holding pre-rebase copies of revisions now in `main`.
Nothing is lost; the bookmark is only keeping the old copies visible. Deleting
it changes a shared remote, so confirm with the user first. A remote bookmark
with no local counterpart must be tracked before the deletion can propagate:

```sh
jj bookmark track <bookmark>@origin
jj bookmark delete <bookmark>      # `forget` drops jj's record only; the next fetch undoes it
jj git push --deleted
jj git fetch
```

If instead both versions are reachable from `main` (`divergent() & ::main`),
two published commits share a change ID. Leave them and refer to them by
commit ID.
