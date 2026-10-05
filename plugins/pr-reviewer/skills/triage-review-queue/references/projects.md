# Project mapping

The review queue arrives as `owner/name` repos; reviewing needs a local
checkout and the Solo project that owns it. That mapping lives in
`~/.claude/pr-reviewer/projects.json`. Keywords (MUST, MUST NOT, SHOULD) are
normative.

## Format

```json
{
  "projects": [
    {
      "repo": "mongodb/laravel-mongodb",
      "path": "/Users/paulinevos/work/laravel-mongodb",
      "solo_project_id": 14,
      "guidelines": ["AGENTS.md", "CONTRIBUTING.md", ".github/CODEOWNERS"],
      "docs": ["docs/"]
    }
  ]
}
```

- `repo` — the PR's `owner/name`, exactly as `gh` reports it. The match key.
- `path` — absolute path to the local checkout.
- `solo_project_id` — the Solo project whose `path` is that checkout, from
  `list_projects`.
- `guidelines` — repo-relative files the reviewer MUST read before reviewing,
  most authoritative first.
- `docs` — repo-relative directories to search for the parity check. Optional;
  omit when the repo has no docs tree.
- `agent_tool_id` — optional per-project override when the project should be
  reviewed by a runtime other than Claude.

Paths and ids are machine-specific, so the file MUST live outside the plugin
and MUST NOT be committed.

## Filling a gap

When a PR's repo is absent, resolve it rather than guessing — a review run
against the wrong checkout is worse than no review:

1. Find the checkout. `list_projects` gives every Solo project's path; confirm
   a candidate with `git -C <path> remote get-url origin` and match the
   `owner/name`. A repo may be checked out more than once (a security fork, a
   worktree); ask which to use rather than taking the first hit.
2. Detect guidelines from what the repo actually has — `AGENTS.md`,
   `CLAUDE.md`, `CONTRIBUTING.md`, `.github/copilot-instructions.md`,
   `.github/PULL_REQUEST_TEMPLATE.md`. List what you found and let the user
   confirm the set and its order.
3. Show the proposed entry, then add it on approval. Create the file with a
   `projects` array when it does not exist yet.

When no checkout exists, say so and ask whether to clone or skip that PR. You
MUST NOT clone without being asked.
