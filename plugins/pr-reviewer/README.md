# pr-reviewer

Claude Code plugin that turns "PRs are waiting on my review" into reviews
drafted by each project's own rules — and never posts anything you have not
read.

| Skill | Use when |
| --- | --- |
| `triage-review-queue` | Finding what awaits your review, classifying it to a project, dispatching reviewers |
| `review-pull-request` | Reviewing one PR: project guidelines, docs parity, scope creep, planned comments |
| `collect-review-findings` | Approving planned comments, then posting them |

`/review-queue [repo | PR | author] [--all]` runs the triage.

## How it works

`triage-review-queue` lists open PRs requesting your review
(`gh search prs --review-requested=@me`), classifies each to its local checkout
and **Solo project**, and spawns one reviewer agent per PR *inside that
project* — so the reviewer inherits the project's environment and tooling, not
the orchestrator's.

Each reviewer follows `review-pull-request`: it reads the project's own
guideline files first (`AGENTS.md`, `CONTRIBUTING.md`, …) and lets them outrank
its defaults, checks the docs did not go stale, and reads the issue the PR
closes to flag changes the issue does not explain. It writes findings to a Solo
scratchpad and stops. It does not post, push, or fix.

`collect-review-findings` shows you every planned comment in full, takes your
edits, and posts only what you approve — per PR, every time.

## Configuration

Repo → checkout → Solo project lives in `~/.claude/pr-reviewer/projects.json`
(machine-specific, never committed):

```json
{
  "projects": [
    {
      "repo": "mongodb/laravel-mongodb",
      "path": "/Users/you/work/laravel-mongodb",
      "solo_project_id": 14,
      "guidelines": ["AGENTS.md", "CONTRIBUTING.md"],
      "docs": ["docs/"]
    }
  ]
}
```

An unmapped repo is resolved interactively — Claude finds the checkout via
Solo's project list, confirms it by git remote, proposes the guideline files it
found, and adds the entry once you approve. Full format and rules:
`skills/triage-review-queue/references/projects.md`.

**Requires** the `gh` CLI (authenticated) and the Solo MCP server. Without
Solo, the skills still work for a single PR in the current checkout; the
per-project dispatch is what Solo provides.

## Running it on a schedule

The plugin has no daemon — triage runs when you ask. To have it check for you,
wrap the command in a routine:

```
/schedule create "weekday mornings, run /review-queue and tell me what is new"
```

or `/loop 30m /review-queue` within a session. Both leave the dispatch decision
with you.

## Install

```sh
npx skills add paulinevos/claude-stuff -s review-pull-request
```

```
/plugin marketplace add paulinevos/claude-stuff
/plugin install pr-reviewer@vos
```
