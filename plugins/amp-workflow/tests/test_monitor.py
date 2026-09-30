import argparse
from decimal import Decimal
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/amp-usage-watch/scripts/monitor.py'
spec = importlib.util.spec_from_file_location('monitor', SCRIPT)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class ParsingTests(unittest.TestCase):
    # Synthetic format cases, not claimed as authenticated CLI captures.
    def test_credit_and_allowance_are_separate(self):
        credits, allowance = monitor.account_usage('\x1b[32mCredit balance: $1,234.50\x1b[0m\nEntitlement: $2.50 remaining of $50.00 limit\nUsage: $999.00')
        self.assertEqual(list(credits.values()), [Decimal('1234.50')])
        self.assertEqual(list(allowance.values()), [Decimal('5')])

    def test_negative_credit_alerts(self):
        credits, _ = monitor.account_usage('Credit balance: $-1.00')
        self.assertEqual(list(credits.values()), [Decimal('-1')])
        credits, _ = monitor.account_usage('Credits: $5.00')
        self.assertEqual(list(credits.values()), [Decimal('5')])

    def test_unknown_or_ambiguous_is_never_zero(self):
        for text in ['Usage: $3', 'Not authenticated', 'Remaining credits: $2 / $10', '']:
            with self.subTest(text=text), self.assertRaises(monitor.MonitorError):
                monitor.account_usage(text)
        for text in ['Total: $1\nTotal: $2', 'Usage unavailable', 'Model: $4', 'Total: $-2']:
            with self.subTest(text=text), self.assertRaises(monitor.MonitorError):
                monitor.thread_usage(text)

    def test_thread_total_not_model_breakdown(self):
        self.assertEqual(monitor.thread_usage('Model X: $99\nTotal: $2.35 USD'), Decimal('2.35'))
        self.assertEqual(monitor.thread_usage('No usage recorded for this thread yet.'), Decimal(0))

    def test_custom_patterns_require_unambiguous_numeric_value(self):
        self.assertEqual(monitor.thread_usage('Billed USD 8.40', r'^Billed USD ([\d.]+)$'), Decimal('8.40'))
        for pattern in [r'(USD)', r'([\d.]+)', r'[', r'(Billed) (USD)']:
            with self.subTest(pattern=pattern), self.assertRaises(monitor.MonitorError):
                monitor.thread_usage('Billed USD 8.40\nBilled USD 2.00', pattern)

    def test_invalid_values(self):
        for value in ['NaN', 'Infinity', '-1']:
            with self.assertRaises(argparse.ArgumentTypeError):
                monitor.amount(value)
        with self.assertRaises(monitor.MonitorError):
            monitor.account_usage('Entitlement: $6 remaining of $5 limit')
        self.assertEqual(monitor.normalize_thread('https://ampcode.com/threads/T-abc-123'), 'T-abc-123')
        with self.assertRaises(argparse.ArgumentTypeError):
            monitor.normalize_thread('T-abc; touch /tmp/evil')


class AlertTests(unittest.TestCase):
    def test_crossings_rearm_and_delivery_failures_retry(self):
        sent = []
        deliver = lambda text: sent.append(text) or True
        state = monitor.alert_changes({'credits': (True, 'low')}, {}, deliver)
        state = monitor.alert_changes({'credits': (True, 'still low')}, state, deliver)
        self.assertEqual(sent, ['low'])
        state = monitor.alert_changes({'credits': (False, 'refilled')}, state, deliver)
        state = monitor.alert_changes({'credits': (True, 'low again')}, state, deliver)
        self.assertEqual(sent, ['low', 'low again'])
        failed = monitor.alert_changes({'thread': (True, 'cap')}, {}, lambda _: False)
        self.assertFalse(failed.get('thread', False))
        monitor.alert_changes({'thread': (True, 'retry')}, failed, deliver)
        self.assertEqual(sent[-1], 'retry')

    def test_exact_cap_and_low_threshold(self):
        options = monitor.parser().parse_args(['check', '--thread', 'T-abc', '--cap', '10'])
        options.amp = 'amp'
        with patch.object(monitor, 'run_amp', side_effect=['Credit balance: $5\nAllowance: $1 remaining of $10 limit', 'Total: $10']):
            observations, _ = monitor.sample(options)
        self.assertTrue(all(triggered for triggered, _ in observations.values()))

    def test_account_failure_does_not_hide_thread_alert(self):
        options = monitor.parser().parse_args(['check', '--thread', 'T-abc', '--cap', '10'])
        options.amp = 'amp'
        with patch.object(monitor, 'run_amp', side_effect=[monitor.MonitorError('Account unavailable'), 'Total: $12']):
            observations, _, errors = monitor.poll(options)
        self.assertTrue(observations['thread:T-abc'][0])
        self.assertEqual(errors, ['Account unavailable'])

    def test_notification_message_is_data(self):
        message = '" & do shell script "touch /tmp/evil"'
        with patch.object(monitor.subprocess, 'run') as run:
            self.assertTrue(monitor.notify(message, 'macos'))
        argv = run.call_args.args[0]
        self.assertEqual(argv[-1], message)
        self.assertNotIn(message, argv[2])


class LifecycleTests(unittest.TestCase):
    def test_repeated_failures_stop_and_save_unhealthy_status(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'amp'
            fake.write_text('#!/bin/sh\nexit 1\n')
            fake.chmod(0o755)
            result = subprocess.run([sys.executable, str(SCRIPT), 'run', '--amp', str(fake), '--state-dir', directory, '--interval', '0.01', '--max-errors', '2'], capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 1)
            state = json.loads((Path(directory) / 'account/state.json').read_text())
            self.assertEqual(state['consecutive_errors'], 2)
            self.assertIn('stopped', state)
            self.assertNotIn('last_success', state)
            self.assertEqual(result.stdout.count('Usage monitor cannot read usage'), 1)

    def test_background_start_duplicate_status_stop_and_dedup_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fake = base / 'amp'
            fake.write_text('#!/usr/bin/env python3\nimport sys\nprint("Total: $12.00" if "threads" in sys.argv else "Credit balance: $3.00\\nAllowance: $1.00 remaining of $10.00 limit")\n')
            fake.chmod(0o755)
            args = ['--amp', str(fake), '--state-dir', str(base / 'state'), '--thread', 'T-test', '--cap', '10', '--interval', '0.1']
            def command(action):
                return subprocess.run([sys.executable, str(SCRIPT), action, *args], capture_output=True, text=True, timeout=8)
            def stopped():
                for _ in range(40):
                    if not json.loads(command('status').stdout)['running']:
                        return
                    time.sleep(0.1)
                self.fail('Watcher failed to exit')
            try:
                started = command('start')
                self.assertEqual(started.returncode, 0, started.stderr)
                self.assertNotEqual(command('start').returncode, 0)
                for _ in range(40):
                    status = json.loads(command('status').stdout)
                    if status.get('last_success'):
                        break
                    time.sleep(0.1)
                self.assertTrue(status['running'])
                self.assertIn('last_success', status)
                self.assertEqual(command('stop').returncode, 0)
                stopped()
                self.assertEqual(command('start').returncode, 0)
                time.sleep(0.4)
            finally:
                command('stop')
                stopped()
            log = (base / 'state/T-test/monitor.log').read_text()
            self.assertEqual(log.count('T-test: $12.00 spent'), 1)
            self.assertEqual(log.count('Credit balance: $3.00 remaining'), 1)
            self.assertEqual(log.count('10.0% remaining'), 1)

    def test_failed_preflight_does_not_start_background_process(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'amp'
            fake.write_text('#!/bin/sh\nexit 1\n')
            fake.chmod(0o755)
            args = [sys.executable, str(SCRIPT), 'start', '--amp', str(fake), '--state-dir', directory]
            failed = subprocess.run(args, capture_output=True, text=True, timeout=8)
            self.assertEqual(failed.returncode, 1)
            self.assertFalse((Path(directory) / 'account/state.json').exists())


if __name__ == '__main__':
    unittest.main()
