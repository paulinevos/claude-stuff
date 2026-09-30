---
name: amp-usage-watch
description: Monitor Amp credits or allowance and notify when running low, or watch an Amp thread ID or URL against a user-provided USD spending cap. Use when asked to watch Amp usage, set a thread cap alert, inspect a monitor, or stop monitoring.
---

# Watch Amp usage

Use the bundled `scripts/monitor.py` with Python 3.9+ on macOS/Linux. It polls `amp usage` and, for a thread cap, `amp threads usage <id>`. A cap is an alert on total lifetime thread cost, including spending before monitoring started. It does not stop Amp or enforce a spending limit. State and deduplication persist under `~/.local/state/amp-monitor/<name>/`.

Take the thread ID/URL and cap amount from the request. Interpret an unqualified cap as USD, and say so. Ask only if the intended thread or amount is missing or ambiguous. Do not use another currency as USD without resolving that choice. Accept `--notify terminal|macos|both`, defaulting to terminal. Default polling is every 60 seconds, low credits is $5, and low allowance is 10% remaining. Preserve any user-specified thresholds or interval.

Resolve `scripts/monitor.py` relative to this skill, not the user's checkout. Run help when needed. Check authentication and parsing with a single sample before starting a watcher:

```sh
python3 <skill-dir>/scripts/monitor.py check --thread T-actual-id --cap 10
```

This prints measured values and coverage warnings without sending notifications. If authentication fails, help the user sign in via `amp login`. If the CLI output is unfamiliar, inspect `amp usage` and `amp threads usage <id>` directly. Do not invent a balance or cost. A verified `--credit-pattern`, `--allowance-pattern`, or `--thread-pattern` can adapt the parser: each must match exactly once with one numeric capture. Allowance patterns capture percent remaining; money patterns capture USD. Pass patterns as quoted arguments, not shell-generated code.

For live terminal notifications, run in the foreground:

```sh
python3 <skill-dir>/scripts/monitor.py run --thread T-actual-id --cap 10 --notify terminal
```

When the agent must hand control back, start a background watcher:

```sh
python3 <skill-dir>/scripts/monitor.py start --thread T-actual-id --cap 10 --notify both
```

Use the user's chosen notification mode; do not silently switch terminal to macOS. Background terminal output/bells go to `monitor.log`, not a detached user's terminal; report the log path and use foreground execution or `tail -f` for live terminal delivery. macOS notifications use `osascript` and may require execution permission outside a sandbox. Delivery also depends on system notification settings. Background watchers survive this chat ending, but do not automatically restart after logout/reboot.

Thread watchers also check account balances by default. Use `--thread-only` when requested, or when the user wants the thread monitored despite unavailable account data. Account-only monitoring omits both `--thread` and `--cap`. Use `--name` to distinguish configurations; by default a watcher is named after its thread, or `account`. One running watcher is allowed per name. To change a running cap, stop the watcher and wait until status says it has exited before starting a new configuration.

```sh
python3 <skill-dir>/scripts/monitor.py status --thread T-actual-id
python3 <skill-dir>/scripts/monitor.py stop --thread T-actual-id
```

Stop requests end only the watcher, after any in-flight CLI request. Never imply that the Amp agent was stopped. Alerts fire once per threshold crossing and rearm after a balance/allowance recovers. Notification failures retry on later polls. Poll errors are visible and trigger a monitor-health notification; five consecutive failures stop the watcher by default. Check status and logs rather than claiming it is still protecting the budget.

Return the thread, cap in USD, monitored balances/allowance coverage, notification mode, interval, watcher name and status/log paths. Do not launch a watcher merely because someone asks to create this skill or script.
