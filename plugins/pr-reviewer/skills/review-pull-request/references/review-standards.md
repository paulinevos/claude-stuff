# Review standards

What counts as a finding, and the shape findings are written in. Keywords
(MUST, MUST NOT, SHOULD) are normative.

## What is a finding

- A finding MUST rest on one of: a project guideline, a test that fails or is
  missing, a defect you can state as concrete inputs producing a wrong result,
  a doc left stale by the change, or a change the closed issue does not
  explain.
- You MUST NOT raise a finding from personal preference, house style the
  project does not share, or a rewrite that is merely different.
- You MUST NOT restate what the diff does, praise the change, or comment to
  show you read a file.
- Where a project guideline contradicts your defaults, the guideline wins and
  the finding is dropped.
- A finding you cannot attribute MUST be dropped rather than softened into a
  question.

## Severity

- `blocking` — the change is wrong, breaks a documented contract, or violates
  a MUST in the project's guidelines.
- `should-fix` — a real problem the author should address, but not one that
  must hold up the merge.
- `question` — you lack the context to judge, and the author has it. Scope
  findings are usually questions: ask why a file belongs, do not assert it
  does not.

A review SHOULD be short. Several `should-fix` findings on one theme belong in
one comment naming the pattern, not one per occurrence.

## Shape

Write the scratchpad as markdown, one `##` section per comment:

```markdown
# Review: <owner/name>#<number>

<One paragraph: what the PR does, and whether it does it.>

## src/Helpers/QueriesRelationships.php:142 — blocking

**Rests on:** CONTRIBUTING.md, "public helpers validate their arguments"

The ids are passed through unvalidated, so a malformed hex string reaches the
driver and surfaces as a BSON error rather than an argument error.

## tests/Ticket/GH2986Test.php:1 — question

**Rests on:** scope — issue #2986 describes only `whereHas`

This file also changes `morphMany` handling, which the issue does not mention.
Is that needed for the fix, or a separate change?

## Verdict

<blocking count, should-fix count — and what you would do with the PR.>
```

The comment body MUST be written as you would post it to the author: addressed
to them, specific, and explaining why it matters. Omit the `## Verdict`
heading's recommendation if the PR is a draft.

## Boundaries

- You MUST NOT post comments, submit a review, approve, or request changes.
- You MUST NOT push, commit, or amend anything in the checkout.
- You MUST NOT fix what you find — the author fixes it. Suggest the fix in the
  comment when it is short enough to state in a sentence.
- Leave the checkout on the branch you found it on.
