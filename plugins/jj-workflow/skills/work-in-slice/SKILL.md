---
name: work-in-slice
description: "Do one slice of work inside your own Jujutsu (jj) workspace as a worker agent: build a chain of small, individually described revisions, keep the slice's bookmark on the newest one, fold fixes into the revision they belong to, stay current with the base, and hand off cleanly without pushing. Use when you have been given a jj workspace path and a slice or bookmark name, when working in a directory with a .jj folder that is one of several workspaces, or when asked to \"commit this in jj\", \"make granular jj revisions\", \"move the bookmark\", \"squash this into the earlier change\", \"split this revision\". Not for planning slices and creating workspaces (parallel-slices), a stale workspace or divergent change (sync-workspace), or pushing and cleanup (finish-slices)."
---

# work-in-slice

You own one workspace, one bookmark, and the change IDs under it. Nothing
else. Produce a bookmark a reviewer can read revision by revision.

## Steps

1. Orient. `cd <workspace>` and confirm where you are:

   ```sh
   jj workspace root
   jj log -r '@ | @-' --no-graph -T 'change_id.short() ++ " " ++ if(empty, "(empty) ") ++ description.first_line() ++ "\n"'
   ```

   `@` should be empty and sit on your base (`trunk()` or the parent slice's
   bookmark). If it is not, stop and ask the orchestrator.

2. One revision per logical step. Edit, then describe and start the next:

   ```sh
   jj status                                  # snapshots your edits into @, shows what changed
   jj describe -m 'Add retry policy to HttpClient'
   jj new                                     # fresh empty @ on top; the described revision is now @-
   ```

   Subject imperative and capitalised, no trailing period; put the *why* in a
   body after a blank line (`-m $'Subject\n\nBody'`). Every revision must build
   and pass tests on its own.

3. Keep the bookmark on the newest described revision. After the first step:

   ```sh
   jj bookmark create <slice> -r @-
   ```

   After every later step: `jj bookmark move <slice> --to @-`. Bookmarks follow
   rewrites of their target automatically but never advance on `jj new`.

4. Fold fixes into the revision they belong to, never stack "Fix typo":

   | Need | Command |
   | --- | --- |
   | Put the edits in `@` into an earlier revision | `jj squash --into <change-id>` |
   | Route several small fixes to whichever ancestor last touched those lines | `jj absorb` |
   | Move only some files of `@` into an earlier revision | `jj squash --into <change-id> <paths>` |
   | Reword an earlier revision | `jj describe -r <change-id> -m '...'` |
   | Split a revision by path, non-interactively | `jj split -r <change-id> <paths>` |
   | Reorder | `jj rebase -r <change-id> -B <other>` |

   Descendants are rebased and the bookmark follows. Refer to revisions by
   change ID; commit IDs change on every rewrite.

5. Stay current when the base moves:

   ```sh
   jj git fetch
   jj rebase -b <slice> -o <base>              # trunk() or <parent-slice>
   jj log -r 'conflicts() & (<base>..@)'       # must print nothing
   ```

   A conflict does not stop jj; it is recorded in the revision. Resolve it
   where it happened: `jj new <conflicted-change>`, edit the file until the
   markers are gone, `jj squash`, then `jj new <slice>` to return to the tip.
   If any command answers "The working copy is stale", follow `sync-workspace`
   before doing anything else.

6. Hand off. Check, then report; do not push and do not forget the workspace.

   ```sh
   jj status                                                   # "The working copy has no changes"
   jj log -r '(<base>..<slice>) & (conflicts() | description(exact:""))'   # must print nothing
   jj log -r '<base>..<slice>' --no-graph --reversed -T 'change_id.short() ++ " " ++ description.first_line() ++ "\n"'
   ```

   Report the workspace path, the bookmark name, and that list of change IDs
   with subjects.

## Rules you must not break

- Never run jj against another workspace, and never describe, squash, rebase,
  abandon or move anything that is not under your bookmark. Each change and
  bookmark has one owner; rewriting someone else's makes their workspace stale.
- Snapshot before you pause (`jj status` is enough). If a parent slice gets
  rewritten while you hold unsnapshotted edits, recovery turns your `@` into a
  divergent change and the edits leave the working copy.
- Do not use `--ignore-immutable`; `trunk()` is frozen.

## Why `@` stays empty

jj records the working copy into `@` on every command. Keeping `@` as an empty
scratch change on top of the finished chain means a stray `jj status` never
smears half-done edits into a described revision, and the bookmark at `@-`
always points at something complete.
