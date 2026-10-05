---
name: triage-review-queue
description: "Find the pull requests waiting on your review, classify each one to its local checkout and Solo project, and dispatch a reviewer agent per PR that follows that project's own guidelines. Use when asked to check the review queue, triage review requests, see what is waiting on your review, or start reviewing a specific PR someone requested review on."
---

# triage-review-queue

You triage and dispatch; the reviewer agent reads the code. It reviews in the
project's own Solo project so it inherits that project's environment, tooling
and guidelines. Read [projects](references/projects.md) for the config format
and how to fill a gap in it.

1. List what is waiting. Skip drafts unless asked; `@me` resolves to the
   authenticated `gh` account.

   ```sh
   gh search prs --review-requested=@me --state=open --sort=updated \
     --json repository,number,title,url,author,isDraft --limit 50
   ```

   Report "nothing waiting" and stop when the list is empty.
2. Classify each PR against `~/.claude/pr-reviewer/projects.json`, matching on
   `repo` (`owner/name`). Resolve an unmapped repo before dispatching it —
   never review from a guessed path. Show the triage table — PR, title, author,
   project, and any unmapped repos — and let the user choose which to review
   before spawning anything. Dispatch only what they pick.
3. Dispatch one reviewer per chosen PR, into that PR's Solo project:

   ```
   spawn_agent(agent_tool_id=<Claude>, project_id=<solo_project_id>,
               name="review-<repo-name>-<number>")
   send_input(process_id=<returned>, input=<briefing>)
   ```

   Resolve `agent_tool_id` from `list_agent_tools` (`tool_type` `claude` unless
   the project's config names another). Prepend the returned
   `agent_instructions` to the briefing verbatim — they carry the orchestration
   context the agent needs to report back.
4. Brief each reviewer with: its PR URL and number, the repo, the checkout
   path, the guideline files named in the config, the `review-pull-request`
   skill to follow, and the scratchpad name to write findings to
   (`review-<repo-name>-<number>`). One PR per agent; never two PRs in one
   agent, and never a second agent on the same PR.
5. Monitor with `get_process_status` and `get_process_output`; do not send
   further input unless a reviewer asks a question or stalls. When a reviewer
   reports done, read its scratchpad and hand the findings to
   `collect-review-findings`. Close each reviewer's process once its findings
   are collected.

Reviewers never post to GitHub and never push — they plan comments only.
Posting is a separate, approved step (`collect-review-findings`).
