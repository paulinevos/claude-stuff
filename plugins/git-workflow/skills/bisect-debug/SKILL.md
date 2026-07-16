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

1. **Turn the bug into a pass/fail command.**
   - If an existing test already covers it, use that — it should fail at `HEAD`.
   - Otherwise write a throwaway check *outside* the repo, e.g.
     `/tmp/bisect-check.sh`, that reproduces the bug and exits 0 when the
     behavior is good and non-zero when it's bad. Keeping it outside the working
     tree is the trick: it stays put across every checkout, so you never add it
     to the repo or shuffle a test commit through history. `git bisect run`
     executes it from the repo root, so reference repo files by their normal
     paths (and include a build step if the project needs one).
2. **Find a known-good commit.** Check out older commits and run the command
   until it passes; note that commit as `[good-commit]`.
3. **Run the bisect automatically:**
   ```
   git bisect start HEAD [good-commit]
   git bisect run bash /tmp/bisect-check.sh   # or the existing test command
   ```
   Git checks out midpoints and runs the command at each until it reports
   `[bad-commit] is the first bad commit`. Finish with `git bisect reset` to
   return to where you started.
4. **Analyze the culprit.** `git show [bad-commit]` — explain what in it caused
   the regression.
5. **Fix it properly.** Suggest a new bug-fix commit that resolves the bug *and*
   adds a proper regression test committed into the repo, so the behavior is
   protected going forward (the throwaway `/tmp` script was only scaffolding —
   discard it). Always a fresh commit, never a rewrite of the culprit — it is
   almost always already on shared history, which must not be rewritten (others
   may have built on it). Write the fix commit with an imperative subject line
   and a body explaining *why* the bug occurred, not how the diff works.

## Why automate with `bisect run`

Manually marking each midpoint good/bad is slow and error-prone. A scripted
command turns the whole search into one step — you only think at the start (pick
the check and the good commit) and the end (fix the culprit).
