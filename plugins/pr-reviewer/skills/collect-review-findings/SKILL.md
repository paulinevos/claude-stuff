---
name: collect-review-findings
description: "Present a reviewer agent's planned review comments for approval, then post the approved ones to the pull request as inline comments. Use when a dispatched reviewer has finished, when asked to show or post planned review comments, or to submit a drafted review."
---

# collect-review-findings

Findings arrive planned, never posted. You present them, the user decides, and
only then does anything reach GitHub. Posting a review is public and visible to
the PR author — you MUST have explicit approval for this PR, in this run.
Approval of an earlier PR's findings does not carry over.

1. Read the reviewer's scratchpad (`review-<repo-name>-<number>`). When several
   reviewers finished, handle one PR at a time — approval is per PR.
2. Present every finding in full: file, line, severity, what it rests on, and
   the comment body as it would be posted. Do not summarise the bodies away —
   the user is approving the words that get posted. Lead with the blocking
   findings. Say plainly when there are none.
3. Let the user drop, keep, or edit each finding, and say what they want the
   review to be: a plain comment, approval, or changes requested. Ask when
   they have not said — do not infer it from the severities.
4. Post only what survived. Inline comments need the file path and a line in
   the diff:

   ```sh
   gh api repos/<owner>/<name>/pulls/<n>/comments \
     -f body='<comment>' -f commit_id='<head sha>' -f path='<file>' \
     -F line=<line> -f side=RIGHT
   ```

   For one review carrying every comment at once, `POST
   repos/<owner>/<name>/pulls/<n>/reviews` takes a `comments` array plus
   `event` (`COMMENT`, `APPROVE`, `REQUEST_CHANGES`). Get the head sha from
   `gh pr view <n> --json headRefOid`. A comment whose line is not in the diff
   is rejected — post it as a PR-level comment instead of moving it to a line
   it does not belong on.
5. Report what was posted and what was dropped, with the PR URL. Stop there:
   you MUST NOT re-review, reply to the author's responses, or post again
   without a fresh approval.

When the user wants nothing posted, say so and leave the scratchpad intact —
the plan keeps its value as notes for a review they write themselves.
