#!/usr/bin/env python3
"""Poll Amp CLI usage; alert thresholds are not enforced spending limits."""
import argparse
from decimal import Decimal, InvalidOperation
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
NUMBER = r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?'
MONEY = rf'\$\s*({NUMBER})(?:\s*USD)?'


class MonitorError(Exception):
    pass


def amount(value):
    try:
        result = Decimal(value.replace(',', ''))
    except (InvalidOperation, AttributeError):
        raise argparse.ArgumentTypeError('Expected a finite USD amount')
    if not result.is_finite() or result < 0:
        raise argparse.ArgumentTypeError('Expected a nonnegative finite USD amount')
    return result


def positive(value):
    result = float(value)
    if not 0 < result < float('inf'):
        raise argparse.ArgumentTypeError('Expected a positive finite number')
    return result


def normalize_thread(value):
    match = re.fullmatch(r'(?:https://ampcode\.com/threads/)?(T-[A-Za-z0-9-]+)(?:/)?', value)
    if not match:
        raise argparse.ArgumentTypeError('Expected an Amp thread ID or https://ampcode.com/threads/T-… URL')
    return match[1]


def custom_amount(text, pattern):
    try:
        matches = list(re.finditer(pattern, text, re.I | re.M))
        if len(matches) != 1 or matches[0].lastindex != 1:
            raise MonitorError('Custom pattern must match exactly once with one numeric capture group')
        return amount(matches[0].group(1))
    except (re.error, argparse.ArgumentTypeError) as exc:
        raise MonitorError(f'Invalid usage pattern/value: {exc}') from exc


def account_usage(text, credit_pattern=None, allowance_pattern=None):
    """Parse labeled USD balances and remaining/limit allowance, never arbitrary dollars."""
    text = ANSI.sub('', text)
    credits, allowances = {}, {}
    for line in text.splitlines():
        line = line.strip()
        # A remaining amount out of a limit is an allowance, not purchased credits.
        allowance = re.search(rf'{MONEY}\s+remaining\s+(?:out\s+)?of\s+{MONEY}\s*(?:limit)?', line, re.I)
        if allowance:
            remaining, limit = map(lambda x: Decimal(x.replace(',', '')), allowance.groups())
            if remaining < 0 or limit <= 0 or remaining > limit:
                raise MonitorError('Invalid remaining/limit allowance in Amp output')
            label = line[:allowance.start()].rstrip(': ') or 'Allowance'
            if label in allowances:
                raise MonitorError('Ambiguous repeated allowance label')
            allowances[label] = remaining / limit * 100
            continue
        balance_label = re.search(r'credits?|balance', line, re.I) and re.search(r'remain|balance|available', line, re.I)
        plain_credits = re.fullmatch(rf'(?:Purchased\s+)?Credits?\s*:\s*{MONEY}', line, re.I)
        if balance_label or plain_credits:
            values = re.findall(MONEY, line, re.I)
            if len(values) == 1:
                label = re.sub(MONEY, '', line, flags=re.I).strip(' :') or 'Credits'
                if label in credits:
                    raise MonitorError('Ambiguous repeated credit balance label')
                credits[label] = Decimal(values[0].replace(',', ''))
    if credit_pattern:
        credits = {'Configured credit balance': custom_amount(text, credit_pattern)}
    if allowance_pattern:
        remaining_percent = custom_amount(text, allowance_pattern)
        if remaining_percent > 100:
            raise MonitorError('Allowance remaining percentage exceeds 100')
        allowances = {'Configured allowance': remaining_percent}
    if not credits and not allowances:
        raise MonitorError('Unrecognized account usage output; inspect amp usage and configure patterns. No balance was assumed.')
    return credits, allowances


def thread_usage(text, pattern=None):
    text = ANSI.sub('', text)
    if pattern:
        return custom_amount(text, pattern)
    matches = re.findall(rf'^\s*(?:Total(?:\s+(?:cost|usage|spent))?|Thread\s+cost|Cost)\s*:\s*{MONEY}\s*$', text, re.I | re.M)
    if len(matches) == 1:
        result = Decimal(matches[0].replace(',', ''))
        if result < 0:
            raise MonitorError('Negative thread cost in Amp output')
        return result
    if text.strip() == 'No usage recorded for this thread yet.':
        return Decimal(0)
    raise MonitorError('Unrecognized or ambiguous thread cost; inspect amp threads usage and configure --thread-pattern. No cost was assumed.')


def find_amp(explicit=None):
    if explicit:
        result = shutil.which(explicit)
        if result:
            return result
        raise MonitorError(f'Amp executable unavailable: {explicit}')
    result = shutil.which('amp')
    if result:
        return result
    for candidate in (Path.home() / '.local/bin/amp', Path.home() / '.amp/bin/amp'):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise MonitorError('Amp CLI is not installed or executable')


def run_amp(amp, args):
    try:
        process = subprocess.run([amp, '--no-color', *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MonitorError(f'Amp command failed: {exc}') from exc
    if process.returncode:
        # Avoid printing command output which could contain credentials or diagnostic state.
        raise MonitorError(f'amp {" ".join(args)} exited {process.returncode}; check amp login and run the command directly')
    return process.stdout


def sample(options):
    observations, warnings = {}, []
    if not options.thread_only:
        credits, allowances = account_usage(run_amp(options.amp, ['usage']), options.credit_pattern, options.allowance_pattern)
        for label, remaining in credits.items():
            observations[f'credits:{label}'] = (remaining <= options.credits_below, f'{label}: ${remaining:,.2f} remaining (threshold ${options.credits_below:,.2f})')
        for label, remaining in allowances.items():
            observations[f'allowance:{label}'] = (remaining <= options.allowance_below_percent, f'{label}: {remaining:.1f}% remaining (threshold {options.allowance_below_percent}%)')
        if not credits:
            warnings.append('No recognized purchased-credit balance; only reported allowance is monitored')
        if not allowances:
            warnings.append('No recognized allowance; only reported credit balances are monitored')
    if options.thread:
        spent = thread_usage(run_amp(options.amp, ['threads', 'usage', options.thread]), options.thread_pattern)
        observations[f'thread:{options.thread}'] = (spent >= options.cap, f'{options.thread}: ${spent:,.2f} spent, cap ${options.cap:,.2f}; https://ampcode.com/threads/{options.thread}')
    return observations, warnings


def poll(options):
    """Keep a failing account query from suppressing thread-cap alerts, and vice versa."""
    from copy import copy
    observations, warnings, errors = {}, [], []
    if not options.thread_only:
        account = copy(options)
        account.thread = None
        try:
            values, notes = sample(account)
            observations.update(values)
            warnings.extend(notes)
        except MonitorError as exc:
            errors.append(str(exc))
    if options.thread:
        thread = copy(options)
        thread.thread_only = True
        try:
            values, notes = sample(thread)
            observations.update(values)
            warnings.extend(notes)
        except MonitorError as exc:
            errors.append(str(exc))
    return observations, warnings, errors


def notify(message, mode):
    print(message, flush=True)
    if mode in ('terminal', 'both'):
        print('\a', end='', flush=True)
    if mode in ('macos', 'both'):
        # Message is argv data, never interpolated into AppleScript source.
        script = 'on run argv\ndisplay notification (item 1 of argv) with title "Amp usage monitor"\nend run'
        try:
            subprocess.run(['osascript', '-e', script, message], check=True, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError) as exc:
            print(f'Notification delivery failed: {type(exc).__name__}; alert remains in this log', file=sys.stderr, flush=True)
            return False
    return True


def alert_changes(observations, previous, deliver):
    updated = dict(previous)
    for key, (triggered, message) in observations.items():
        if triggered and not previous.get(key, False):
            if deliver(message):
                updated[key] = True
        elif not triggered:
            updated[key] = False  # Reset when credits refill or allowance renews.
    return updated


def paths(options):
    base = options.state_dir.expanduser() / options.name
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    return base


def running(base):
    with (base / 'lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def load_state(base):
    try:
        data = json.loads((base / 'state.json').read_text())
        if not isinstance(data, dict) or not isinstance(data.get('alerts', {}), dict):
            raise ValueError('Invalid state structure')
        return data
    except FileNotFoundError:
        return {}
    except (ValueError, OSError) as exc:
        raise MonitorError(f'Cannot read monitor state: {exc}') from exc


def save_state(base, state):
    temp = base / 'state.tmp'
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(base / 'state.json')


def loop(options):
    base = paths(options)
    with (base / 'lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise MonitorError(f'Monitor {options.name} is already running')
        (base / 'stop').unlink(missing_ok=True)
        state = load_state(base)
        identity = [options.amp, options.thread, str(options.cap), str(options.credits_below), str(options.allowance_below_percent), options.thread_only, options.credit_pattern, options.allowance_pattern, options.thread_pattern]
        previous = state.get('alerts', {}) if state.get('identity') == identity else {}
        state = {'pid': os.getpid(), 'identity': identity, 'alerts': previous, 'started': time.time()}
        save_state(base, state)
        errors, last_warnings = 0, None
        try:
            while not (base / 'stop').exists():
                try:
                    observations, warnings, failures = poll(options)
                    previous = alert_changes(observations, previous, lambda message: notify(message, options.notify))
                    state['alerts'] = previous
                    if warnings != last_warnings:
                        for warning in warnings:
                            print(f'Warning: {warning}', file=sys.stderr, flush=True)
                        last_warnings = warnings
                    if failures:
                        raise MonitorError('; '.join(failures))
                    if errors:
                        print('Usage polling recovered', flush=True)
                    errors = 0
                    state.update(alerts=previous, last_success=time.time(), error=None, consecutive_errors=0)
                except MonitorError as exc:
                    errors += 1
                    state.update(error=str(exc), consecutive_errors=errors)
                    print(f'Polling error: {exc}', file=sys.stderr, flush=True)
                    if errors == 1:
                        notify(f'Usage monitor cannot read usage: {exc}', options.notify)
                save_state(base, state)
                if errors >= options.max_errors:
                    raise MonitorError(f'Stopped after {errors} consecutive polling failures; inspect the log and restart')
                deadline = time.monotonic() + options.interval
                while time.monotonic() < deadline and not (base / 'stop').exists():
                    time.sleep(min(1, max(0, deadline - time.monotonic())))
        finally:
            state['stopped'] = time.time()
            save_state(base, state)


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('action', choices=['check', 'run', 'start', 'status', 'stop'])
    cli.add_argument('--thread', type=normalize_thread, help='Amp thread ID or URL')
    cli.add_argument('--cap', type=amount, help='Alert when total lifetime thread cost reaches this USD amount')
    cli.add_argument('--credits-below', type=amount, default=Decimal('5'), help='Alert at or below this USD credit balance (default 5)')
    cli.add_argument('--allowance-below-percent', type=amount, default=Decimal('10'), help='Alert at or below this percent remaining (default 10)')
    cli.add_argument('--thread-only', action='store_true', help='Skip account balance and allowance checks')
    cli.add_argument('--notify', choices=['terminal', 'macos', 'both'], default='terminal')
    cli.add_argument('--interval', type=positive, default=60, help='Seconds between polls (default 60)')
    cli.add_argument('--max-errors', type=int, default=5, help='Stop after this many consecutive failures (default 5)')
    cli.add_argument('--amp', help='Amp executable path')
    cli.add_argument('--name', default=None, help='Monitor name for start/status/stop; defaults to thread ID or account')
    cli.add_argument('--state-dir', type=Path, default=Path.home() / '.local/state/amp-monitor')
    cli.add_argument('--credit-pattern', help='Regex matching exactly one balance with one numeric USD capture')
    cli.add_argument('--allowance-pattern', help='Regex matching exactly one remaining percentage with one numeric capture')
    cli.add_argument('--thread-pattern', help='Regex matching exactly one total thread USD cost with one numeric capture')
    return cli


def main(argv=None):
    cli = parser()
    options = cli.parse_args(argv)
    options.name = options.name or options.thread or 'account'
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', options.name):
        cli.error('Monitor name must use letters, digits, underscores, or hyphens')
    if options.action in ('check', 'run', 'start'):
        if bool(options.thread) != (options.cap is not None):
            cli.error('--thread and --cap must be provided together')
        if options.thread_only and not options.thread:
            cli.error('--thread-only requires --thread and --cap')
        if options.allowance_below_percent > 100:
            cli.error('--allowance-below-percent cannot exceed 100')
        if options.max_errors < 1:
            cli.error('--max-errors must be positive')
        if options.notify in ('macos', 'both') and sys.platform != 'darwin':
            cli.error('macOS notifications require macOS; use --notify terminal')
        options.amp = find_amp(options.amp)
    if options.action == 'check':
        observations, warnings = sample(options)
        for _, (triggered, message) in observations.items():
            print(f'{"ALERT" if triggered else "OK"}: {message}')
        for warning in warnings:
            print(f'Warning: {warning}', file=sys.stderr)
        return 0
    base = paths(options)
    if options.action == 'status':
        print(json.dumps({'running': running(base), 'name': options.name, 'log': str(base / 'monitor.log'), **load_state(base)}, indent=2))
        return 0
    if options.action == 'stop':
        if running(base):
            (base / 'stop').touch()
            print('Stop requested; the monitor exits after its current CLI request (up to 30 seconds). Amp threads keep running.')
        else:
            print('Monitor is not running')
        return 0
    if options.action == 'run':
        loop(options)
        return 0
    if running(base):
        raise MonitorError(f'Monitor {options.name} is already running')
    # Validate authentication and output before claiming a background monitor started.
    sample(options)
    args = list(sys.argv[1:] if argv is None else argv)
    args[0] = 'run'
    if '--amp' not in args:
        args.extend(['--amp', options.amp])
    with (base / 'monitor.log').open('a') as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), *args], stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    for _ in range(30):
        time.sleep(0.1)
        if process.poll() is not None:
            raise MonitorError(f'Monitor failed to start; inspect {base / "monitor.log"}')
        if running(base):
            print(f'Started {options.name} (PID {process.pid}); log: {base / "monitor.log"}')
            if options.notify in ('terminal', 'both'):
                print('Background terminal notifications go to the log. For live terminal alerts, run in the foreground or tail -f the log.')
            return 0
    raise MonitorError(f'Monitor startup could not be confirmed; inspect {base / "monitor.log"} before retrying')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (MonitorError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
