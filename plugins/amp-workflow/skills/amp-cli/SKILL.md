---
name: amp-cli
description: Use ampcode.com's CLI when the user asks to start an orb or thread on Amp, hand work to Amp with summarized context, continue a thread, or inspect and manage Amp work.
---

# Amp CLI

When asked to start an orb, start a thread on Amp, or hand work to Amp, actually launch it through the CLI and return its URL. Writing this skill does not itself authorize launching an Amp task.

## Check availability

Run `command -v amp`, `amp version`, and `amp --help`. If PATH misses it, check `~/.local/bin/amp` and `~/.amp/bin/amp`. Read relevant subcommand help for unfamiliar operations: Amp changes quickly.

If missing, report it. When installation is requested, download and inspect `https://ampcode.com/install.sh`, run the official installer with required permissions, and verify help/version. Existing shells may need the absolute executable path after the installer updates PATH.

Check `amp account list`. An existing `AMP_API_KEY` can authenticate too; check presence without revealing its value. If needed, use `amp login` when authorized and leave browser sign-in to the user. Successful help output does not establish authentication.

## Prepare context

Write a self-contained summary to a temporary UTF-8 file using a file-writing tool. Include the outcome and acceptance criteria, repository/project and branch or commit, relevant files and links, decisions and constraints, findings, completed work, next steps, reproduction/tests and known failures, and the scope of authorized actions. Distinguish facts from hypotheses. Omit unrelated history and credentials. Feed this file through stdin rather than interpolating conversation text into a shell command.

Run in the relevant checkout. For repository work, check `amp projects status --json` or select a known project explicitly; resolve a missing project before launching. No-project orbs are appropriate for tasks needing no repository. Orbs cannot assume access to local paths, uncommitted changes, or unpublished commits. Supply necessary diffs/files through prompt context or `--attach` and explain their use. Do not push merely to facilitate a handoff without authorization.

## Launch and follow up

For an orb or a generic remote handoff to a thread on Amp, use:

```sh
amp -ox --title 'Investigate the failing build' --project owner/repo < /tmp/amp-handoff.txt
```

Replace examples with actual values. `-ox` submits the prompt and returns a thread URL while work continues remotely. Report launched work, not completed work. Preserve requested mode, visibility, and orb size; otherwise use defaults. Do not silently change a requested executor.

For explicitly local work:

```sh
amp -x --executor local --no-archive-after-execute --stream-json < /tmp/amp-handoff.txt
```

This waits for the turn. Extract the thread ID from structured output according to the installed version's schema. For a specified runner, use `--executor runner:<id>` and optionally `--runner-dir <absolute-path>`.

Follow up on a known remote thread without creating another:

```sh
amp threads continue T-actual-id -ox < /tmp/amp-followup.txt
```

Use `-x` for existing local work. `amp threads new` creates an empty thread: use only when an empty thread is requested. Interactive `amp --executor orb` waits for the first prompt and is unsuitable for an unattended launch. If submission is uncertain, inspect recent threads before retrying. Add `--no-archive-after-execute` when streaming an orb turn that should stay active.

## Manage Amp

Check each command's `--help` for exact arguments.

| Need | Commands |
| --- | --- |
| Find work | `amp threads list`, `amp threads search`, `amp top` |
| Read results | `amp threads markdown <id>`, `amp threads export <id>` |
| Costs/context | `amp usage`, `amp threads usage <id>`, `amp threads context <id>` |
| Projects | `amp projects status --json`, `amp projects list`, `amp projects get` |
| Organization | `amp threads rename`, `amp threads label`, `amp threads archive` |
| Integrations | `amp tools list`, `amp plugins list`, `amp skill list`, `amp mcp doctor` |

Sharing, deletion, account switching, and changing projects/integrations need corresponding user intent. Orb service commands manage processes inside an orb; do not assume they target a remote orb from a local checkout. Verify synchronization support in installed help before applying remote changes locally.

For cap alerts, use the sibling [amp-usage-watch skill](../amp-usage-watch/SKILL.md). Consult the official [CLI](https://ampcode.com/docs/cli), [orb](https://ampcode.com/docs/cli/spawning-orbs), and [thread](https://ampcode.com/docs/threads) docs when help is insufficient.
