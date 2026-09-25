---
name: work-in-slice
description: "Do one owned slice in a Jujutsu workspace: make granular described revisions, keep its bookmark at the tip, fold fixes into their revision, rebase safely, and hand off without publishing."
---

# work-in-slice

Own only the assigned workspace, bookmark, and descendant change IDs. Work
there, never in another worker's directory.

1. Confirm `@` is an empty change on the assigned base:

   ```sh
   jj workspace root
   jj log -r '@ | @-' --no-graph -T 'change_id.short() ++ " " ++ if(empty, "(empty) ") ++ description.first_line() ++ "\n"'
   ```

   If it is not, stop and tell the orchestrator.
2. Make one logical, independently passing revision at a time:

   ```sh
   jj status
   jj describe -m 'Add retry policy to HttpClient'
   jj new
   ```

   Use an imperative, capitalised subject without a period; a body explains
   why. Create the bookmark after the first revision with
   `jj bookmark create <slice> -r @-`, then move it after every revision with
   `jj bookmark move <slice> --to @-`.
3. Fold fixes rather than stacking follow-ups: `jj squash --into <change-id>`;
   use `jj absorb` for line-based ancestor fixes, `jj split` to separate work,
   `jj describe -r` to reword, and `jj rebase -r ... -B ...` to reorder. Refer
   to revisions by change ID, not commit ID.
4. When the base moves: `jj git fetch && jj rebase -b <slice> -o <base>`;
   resolve recorded conflicts in their revision (`jj new`, edit, `jj squash`),
   then return to the tip with `jj new <slice>`. A stale-workspace error means
   stop and use `sync-workspace`.
5. Before hand-off, leave `@` empty, run `jj status`, ensure all slice revisions
   are described and conflict-free, and report the workspace, bookmark, and
   ordered revision list. Do not push or forget the workspace.

Never use `--ignore-immutable`. Snapshot with `jj status` before pausing;
rewriting an active descendant's ancestor risks a divergent recovery.
