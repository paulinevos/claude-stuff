---
name: maintain-atomic-commits
description: "Keep history as atomic commits by folding a change into the existing commit it belongs to instead of stacking a new one — the heart of an atomic-commit workflow. Use whenever an uncommitted (or about-to-be-made) change is really a fix, tweak, reword, or addition to a commit already on the branch: a typo or forgotten file in the commit just made, a correction belonging in a commit from further back, or several working-tree edits that each belong to different earlier commits. It routes to the right mechanism automatically: `git commit --amend` for the latest commit, an interactive-rebase `edit` stop for authoring into an older commit in its own context, or `git commit --fixup` + autosquash for already-made changes (especially when they map to several target commits). Common phrasings: \"fold this into my last commit\", \"this fix belongs in the commit where I added X\", \"reword the last commit\", \"these edits fix a couple of earlier commits, squash them in\", \"get this into that commit so history looks clean\". Not for making a brand-new commit, rebasing onto a base branch, or resolving conflicts on their own."
---

# maintain-atomic-commits

When a change belongs to a commit that already exists, fold it in rather than
leaving a "fix typo" follow-up (see [conventions](../../references/conventions.md)
for why). This skill picks the mechanism by *where* the change goes and *when*
you made it.

## First: which commit does the change belong to?

List what's still local and safe to rewrite with `git log --oneline [base]..HEAD`.
You MUST NOT rewrite a commit already on a shared branch (see
[conventions](../../references/conventions.md)).

Then route:

| Situation | Go to |
| --- | --- |
| Belongs in the **latest** commit (`HEAD`) | **A — amend** |
| Belongs in an **older** commit, and you haven't written the change yet | **B — edit in place** |
| Belongs in older commit(s), and you've **already made** the change (maybe spanning several commits) | **C — fixup + autosquash** |

If two situations seem to fit, prefer the simplest that applies: A over B over C.

## A — amend the latest commit

Cheapest case: nothing is stacked on `HEAD`, so just absorb the change.

1. Confirm it belongs in `HEAD`, not earlier: `git log --oneline -5`,
   `git show HEAD`.
2. Stage it: `git add [paths]` (or `git add -p` for specific hunks).
3. `git commit --amend` (reword if the change alters what the commit does;
   `--no-edit` to keep the message). Rewording alone is `git commit --amend` too.

## B — edit an older commit in its own context

Use this when you want to *author* the change as if you were back at that
commit — e.g. you need the working tree in that commit's state to run its tests,
or the change is interdependent and awkward to isolate as a clean hunk later.

1. `git rebase -i HEAD~[n]` (or `git rebase -i [base-branch]`).
2. Change the target commit's prefix from `pick` to `e` (edit); save. Git stops
   with that commit checked out.
3. Make and stage the change, then `git commit --amend` (reword if needed).
4. `git rebase --continue` to replay the rest. If replay conflicts, resolve it
   (see `resolve-merge-conflict`) and continue.

## C — route already-made changes with fixup + autosquash

Use this when the change already exists in the working tree and belongs in one
or more *earlier* commits. It records each change against its target now and
defers the rewrite to a single autosquash pass — no per-commit rebase stops.

1. For each target commit, stage only its hunks — `git add -p [file]` when one
   file has changes destined for different commits — then
   `git commit --fixup [commit-id]`.
2. Repeat until every change is recorded. Show the user the resulting `fixup!`
   commits and confirm the mapping.
3. Autosquash: `git rebase -i --autosquash [base-branch]` (or `HEAD~[n]`). Git
   pre-arranges each fixup under its target; just save to apply.
4. Expect possible conflicts. Folding into an older commit replays every later
   commit on top of the changed code, so a fix near lines a later commit also
   touched will conflict — this is normal. Resolve each (see
   `resolve-merge-conflict`) and `git rebase --continue`.

### Example (case C): two commits, one dirty file

- Commit 1 changes a method signature in `Foo.php`; commit 2 adds a method in
  `Foo.php`.
- Uncommitted: a typo fix in the signature (→ commit 1) and error handling in
  the new method (→ commit 2).
- `git add -p Foo.php` to stage the signature hunk → `git commit --fixup <c1>`;
  stage the error-handling hunk → `git commit --fixup <c2>`; then autosquash.
