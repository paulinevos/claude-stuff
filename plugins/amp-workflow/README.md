# Amp workflow

Launch Amp threads with summarized context and monitor account credits, allowance,
and total thread spending. Requires the Amp CLI and Python 3.9+ on macOS/Linux.

| Skill | Use when |
| --- | --- |
| [amp-cli](skills/amp-cli/SKILL.md) | Start an orb/thread on Amp, hand off context, continue or manage work |
| [amp-usage-watch](skills/amp-usage-watch/SKILL.md) | Watch credits/allowance or a thread against a USD alert cap |

Install from this repository's `vos` marketplace:

```text
/plugin install amp-workflow@vos
```

The portable `plugin.json` also describes this local skills plugin. Its skills and
supporting script live together so individual skill installs retain the monitor.

Sign in with `amp login`. The monitor invokes the CLI with the current account;
changing accounts while a watcher runs can change what it measures. Stop watchers
before switching accounts.

```sh
python3 skills/amp-usage-watch/scripts/monitor.py check --thread T-THREAD-ID --cap 10
python3 skills/amp-usage-watch/scripts/monitor.py run --thread T-THREAD-ID --cap 10
python3 skills/amp-usage-watch/scripts/monitor.py start --thread T-THREAD-ID --cap 10 --notify macos
python3 skills/amp-usage-watch/scripts/monitor.py status --thread T-THREAD-ID
python3 skills/amp-usage-watch/scripts/monitor.py stop --thread T-THREAD-ID
```

Run those commands from this plugin directory or use the script's absolute path.
Omit `--thread` and `--cap` to monitor account usage only. Add `--thread-only` to
skip account checks. Caps use total lifetime thread cost in USD; they notify and
never interrupt the thread. Default credit warning is $5 or less, allowance is
10% remaining or less, and polling is every 60 seconds. Configure with
`--credits-below`, `--allowance-below-percent`, and `--interval`.

`--notify terminal|macos|both` defaults to terminal (text and bell). Background
terminal output goes to the monitor log; use `run` or `tail -f` for live terminal
alerts. macOS uses native notifications through `osascript`; system permissions
and notification settings apply. Watchers do not restart automatically at reboot.
`status` reports a process lock, last successful poll, and errors, not just a PID.
`stop` requests a clean exit after any current request, which can take 30 seconds.

The installed Amp CLI provides human-readable usage, without a documented JSON
usage flag. The parser accepts explicitly labeled dollar balances, remaining/limit
allowance lines, and labeled thread totals, rejecting unfamiliar/ambiguous output.
Missing account categories produce coverage warnings. If output changes, inspect
it before using `--credit-pattern`, `--allowance-pattern`, or `--thread-pattern`.
Each regex must match once with one numeric capture; allowance is percent remaining,
other values are USD. Unknown usage is never assumed to be zero. Alerts deduplicate
across polls/restarts and rearm when balances recover. After five consecutive errors,
the watcher stops; its health alert and log explain the failure.

Run the offline verification suite from the repository root:

```sh
python3 -m unittest discover -s plugins/amp-workflow/tests -v
```
