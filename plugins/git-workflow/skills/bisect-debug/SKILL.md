---
name: bisect-debug
description: Find the commit that introduced a regression with an automated git bisect, then make a tested fix. Use when behaviour used to work but the culprit is unknown and can be expressed as a pass/fail command.
---

# bisect-debug

1. Use a failing existing test, or create a throwaway `/tmp/bisect-check.sh`
   that exits 0 for good and non-zero for bad. Keep it outside the repository
   so every bisect checkout can use it.
2. Find and verify a known-good commit, then run:

   ```sh
   git bisect start HEAD <good-commit>
   git bisect run bash /tmp/bisect-check.sh
   ```

3. Inspect the reported first bad commit with `git show`; explain the cause.
   Always finish with `git bisect reset`.
4. Make a new, tested bug-fix commit; never rewrite the culprit on shared
   history. Its imperative message should explain why the regression occurred.
