---
description: Show the pull requests waiting on your review and dispatch reviewer agents for the ones you pick
---

Triage the review queue using the `triage-review-queue` skill.

$ARGUMENTS may narrow what to triage — a repo (`mongodb/laravel-mongodb`), a
single PR (a URL or `owner/name#number`), or an author. With no arguments,
triage the whole open queue. `--all` includes drafts, which are skipped by
default.

Show the triage table and wait for the user to choose before spawning any
reviewer. When a single PR is named, still confirm the project mapping before
dispatching it.
