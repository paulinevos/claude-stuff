---
name: bisect-debug
description: Find the commit that introduced a regression with an automated git bisect run, then fix it. Use when something that used to work is now broken and the cause isn't obvious — the user says "this worked last week", "which commit broke X", "find the commit that caused this bug", "it regressed", or asks to bisect. Best when you can express the bug as a pass/fail command.
---

# bisect-debug

A regression means there's a specific commit where behavior flipped from good to
bad. Bisect finds it in O(log n) steps by binary-searching history with a
pass/fail test. The payoff is a precise culprit commit you can read and fix,
instead of guessing.

## Steps

1. **Get a reliable pass/fail signal.** Bisect is only as good as its test.
   - If a test already covers the regression, run it — it should fail at `HEAD`.
   - If nothing covers it, write a failing regression test that captures the bug
     and commit it. You'll move this commit around, so keep it self-contained.
2. **Find a known-good commit.** Check out candidates back in history and
   confirm the behavior worked there (run the test; if the test commit didn't
   exist yet, temporarily apply/cherry-pick it or move it there with an
   interactive rebase). Note that commit id as `[good-commit]`.
3. **Run the bisect automatically:**
   ```
   git bisect start HEAD [good-commit]
   git bisect run [test-command]
   ```
   `git bisect run` checks out midpoints and runs the command at each until it
   reports `[bad-commit] is the first bad commit`. End with `git bisect reset`.
4. **Analyze the culprit.** `git show [bad-commit]` — explain what in that commit
   caused the regression.
5. **Fix it atomically.** Offer to fix the bug so the regression test passes.
   Once the test commit is back at `HEAD` (interactive rebase to move it if you
   relocated it), fold the fix into the appropriate commit and reword its message
   to describe the fix — or, if the culprit is already public history, make a new
   bug-fix commit instead (see [conventions](../../references/conventions.md) on
   not rewriting shared commits).

## Why automate with `bisect run`

Manually marking each midpoint good/bad is slow and error-prone. A scripted
test command turns the whole search into one command and removes human mistakes
from the bisection — you only think at the start (pick the test and good commit)
and the end (fix the culprit).
