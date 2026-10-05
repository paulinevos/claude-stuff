---
name: review-pull-request
description: "Review one pull request against the project's own coding guidelines, check the docs stayed in parity, read the issue it closes to catch scope creep, and plan inline review comments without posting them. Use when reviewing a PR, when dispatched as a reviewer agent for a PR, or when asked to draft review comments for a change."
---

# review-pull-request

You review one PR, in its own checkout, by that project's rules — not your own
taste. Read [review-standards](references/review-standards.md) before writing
findings. You plan comments; you MUST NOT post them, push, or alter the PR.

1. Read the PR and its diff. Work from the checkout path you were given.

   ```sh
   gh pr view <n> --repo <owner/name> --json title,body,author,isDraft,baseRefName,additions,deletions,changedFiles,closingIssuesReferences
   gh pr diff <n> --repo <owner/name>
   ```

   Check the diff out locally (`gh pr checkout <n>`) only when you must run
   something; stash first and restore the prior branch when done.
2. Read the project's guideline files before judging any line. They outrank
   your defaults and this skill. Where a guideline and your instinct disagree,
   the guideline wins and the finding goes away. Note which guideline a finding
   rests on — a finding you cannot attribute to a guideline, a test, or a
   demonstrable defect is not a finding.
3. Review the diff against those guidelines, reading surrounding files for the
   conventions the diff should match: how siblings are structured, named and
   tested. A change consistent with its neighbours is correct even when you
   would have written it differently.
4. Check docs parity. Search the project's docs for what this change affects —
   behaviour, options, defaults, public API. A behavioural change that leaves
   the docs describing the old behaviour is a finding; so is a new public
   surface documented nowhere. Say which doc file is now stale.
5. Guard against scope creep. Read the issue the PR closes
   (`closingIssuesReferences`, or an issue named in the body) and its linked
   discussion. Map each changed file to the issue's stated problem. Anything
   unexplained by the issue or the PR description is a finding: name the file
   and ask why it belongs, rather than asserting it does not.
6. Plan the comments. Write findings to the scratchpad you were given, in the
   shape [review-standards](references/review-standards.md) specifies — one
   entry per comment, each with file, line, severity, the guideline it rests
   on, and the comment as you would post it. Finish with a short summary: what
   the PR does, whether it does it, and the blocking findings if any.
7. Report that the scratchpad is written and stop. Do not post, approve,
   request changes, or push.
