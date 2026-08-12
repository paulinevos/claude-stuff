---
name: sync-workspace
description: "Bring a Jujutsu (jj) workspace back in step with the shared repository: the error \"The working copy is stale (not updated since operation ...)\", a slice that must be rebased onto a moved base (trunk(), main@origin) or onto a parent slice that grew, a change shown as \"(divergent)\" with /0 /1 offsets, or a bookmark shown with \"??\" (conflicted). Use whenever jj refuses a command with a stale-working-copy error, after jj git fetch moved the base, when a parent slice was rewritten under a dependent one, or when jj log shows divergent or conflicted markers. Not for the conflict markers a rebase you ran yourself left in a file (handled in work-in-slice), planning, or cleanup."
---

# sync-workspace

Four symptoms, four fixes. Identify the symptom first.

| Symptom | Section |
| --- | --- |
| `Error: The working copy is stale (not updated since operation …)` | **A** |
| Base moved (`jj git fetch` updated `main@origin`) or the parent slice grew | **B** |
| `(divergent)` in the log; change IDs shown as `xxxx/0`, `xxxx/1` | **C** |
| Bookmark shown as `name??`, or `jj new name` says it resolved to several revisions | **D** |

## A: stale working copy

Someone rewrote a revision your `@` descends from, from another workspace
(typically a parent slice was squashed or reworded). Your files still show the
old state.

```sh
jj workspace update-stale
jj status
```

`update-stale` snapshots your working copy first and then moves it onto the
rewritten commit. If everything was already snapshotted, that is the end of
it. If you had unsnapshotted edits when the rewrite happened, `jj status` now
shows `@` as `(divergent)` and those edits are missing from the working copy:
continue with **C**. Prevent this by running `jj status` before you pause, and
by never rewriting revisions another active workspace builds on.

## B: rebase onto a moved base or parent slice

```sh
jj git fetch
jj rebase -b <slice> -o <base>              # trunk(), or <parent-slice> for a dependent slice
jj log -r 'conflicts() & (<base>..@)'
```

`-b` rebases the whole slice relative to the destination and leaves the
bookmark on the rebased tip. For each conflicted revision: `jj new <change>`,
edit until the markers are gone, `jj squash`, then `jj new <slice>` to return
to the tip. Rebase only slices you own; rebasing someone else's slice makes
their workspace stale.

## C: divergent change

Two visible commits share one change ID, so the ID alone is ambiguous. List
the versions and what each carries:

```sh
jj log -r 'mutable()' --no-graph -T 'if(divergent, change_id.short() ++ " " ++ commit_id.short() ++ "  " ++ diff.files().map(|f| f.path()).join(" ") ++ "\n")'
```

Then choose:

| Want | Command |
| --- | --- |
| Both sides combined (the usual case after **A**) | `jj squash --from <other-commit-id> --into @` |
| Only one side | `jj abandon <unwanted-commit-id>` |
| Keep both as separate changes | `jj metaedit --update-change-id <commit-id>` |

Confirm with `jj log -r @`: the `(divergent)` label is gone and `jj status`
lists the recovered files.

## D: conflicted bookmark

The bookmark was moved in two places at once (two workspaces, or local and
remote). `jj bookmark list <name>` shows the candidate targets.

```sh
jj bookmark move <name> --to <change-id>     # pick the intended target
jj git fetch                                 # for a conflicted remote bookmark, name@origin
```

If both targets carry wanted work, rebase one onto the other first
(`jj rebase -s <one> -o <other>`), then move the bookmark to the new tip.

## Why these happen at all

jj has no locks. Every workspace loads a consistent view, does its work, and
commits an operation; when two operations race, jj merges them and records
what could not be reconciled as a conflicted bookmark or a divergent change
instead of failing. Nothing is lost, but somebody has to pick. The one-owner
rule (one worker per workspace, bookmark and change) is what keeps these
sections from being needed during normal work.
