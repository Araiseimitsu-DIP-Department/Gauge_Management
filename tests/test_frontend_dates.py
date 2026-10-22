"""実際の日付同期スクリプトをNode.jsで実行し、DBなしで検証する。"""
import os
import shutil
import subprocess
import unittest

from app.webview.frontend_dates import SCRIPT

NODE = shutil.which("node")

HARNESS = r"""
const assert = require('node:assert/strict');
const NativeDate = Date;
let clock = new NativeDate(2026, 9, 22, 23, 59, 59);
global.Date = class extends NativeDate { constructor(...args) { super(...(args.length ? args : [clock])); } };
const state = {
  currentDate: '2026-10-22', startupDate: '2026-10-22',
  lending: {registerDate:'2026-10-22', registerGaugeSizes:['1.230'], registerStaffId:'123'},
  return: {date:'2026-10-22', caseNo:'A1', selectedLoanId:42},
};
const inputs = {lending:{value:'2026-10-22'}, return:{value:'2026-10-22'}};
const windowEvents = {}, documentEvents = {};
let interval, intervalMs;
const window = {
  setInterval: (callback, ms) => { interval = callback; intervalMs = ms; },
  addEventListener: (name, callback) => { windowEvents[name] = callback; },
};
const document = {
  hidden:false,
  querySelector: selector => selector.includes('"lending"') ? inputs.lending : inputs.return,
  addEventListener: (name, callback) => { documentEvents[name] = callback; },
};
"""


@unittest.skipUnless(NODE, "日付同期のJavaScriptテストにはNode.jsが必要です。")
class FrontendDatesTests(unittest.TestCase):
    def run_script(self, scenario):
        result = subprocess.run(
            [NODE, "-"], input=HARNESS + SCRIPT + scenario,
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "TZ": "Asia/Tokyo"},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_same_day_preserves_manual_dates(self):
        self.run_script("""
state.lending.registerDate = inputs.lending.value = '2026-10-10';
state.return.date = inputs.return.value = '';
interval();
assert.equal(state.lending.registerDate, '2026-10-10');
assert.equal(inputs.lending.value, '2026-10-10');
assert.equal(state.return.date, '');
assert.equal(inputs.return.value, '');
""")

    def test_midnight_updates_only_dates_in_local_timezone(self):
        self.run_script("""
clock = new NativeDate(2026, 9, 23, 0, 0, 0);
interval();
assert.equal(intervalMs, 30000);
assert.equal(state.currentDate, '2026-10-23');
assert.equal(state.lending.registerDate, '2026-10-23');
assert.equal(state.return.date, '2026-10-23');
assert.equal(inputs.lending.value, '2026-10-23');
assert.equal(inputs.return.value, '2026-10-23');
assert.equal(state.startupDate, '2026-10-22');
assert.deepEqual(state.lending.registerGaugeSizes, ['1.230']);
assert.equal(state.lending.registerStaffId, '123');
assert.equal(state.return.caseNo, 'A1');
assert.equal(state.return.selectedLoanId, 42);
""")

    def test_resume_after_multiple_days_updates_hidden_screen_state(self):
        self.run_script("""
inputs.lending = null;
clock = new NativeDate(2026, 10, 2, 8, 0, 0);
document.hidden = true;
documentEvents.visibilitychange();
assert.equal(state.currentDate, '2026-10-22');
document.hidden = false;
documentEvents.visibilitychange();
assert.equal(state.lending.registerDate, '2026-11-02');
assert.equal(inputs.return.value, '2026-11-02');
clock = new NativeDate(2027, 0, 1, 0, 0, 0);
windowEvents.focus();
assert.equal(state.return.date, '2027-01-01');
clock = new NativeDate(2027, 0, 2);
windowEvents.pageshow();
assert.equal(state.return.date, '2027-01-02');
""")

    def test_before_bootstrap_does_not_initialize_or_modify_form(self):
        self.run_script("""
state.currentDate = '';
clock = new NativeDate(2026, 9, 23);
interval();
assert.equal(state.currentDate, '');
assert.equal(inputs.lending.value, '2026-10-22');
""")


if __name__ == "__main__":
    unittest.main()
