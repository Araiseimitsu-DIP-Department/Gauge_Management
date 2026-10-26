"""返却ケースNoの画面判定とエラー表示をDBなしで検証する。"""
import shutil
import subprocess
import unittest

from app.webview.frontend_render import SCRIPT as RENDER_SCRIPT
from app.webview.frontend_controller import SCRIPT as CONTROLLER_SCRIPT

NODE = shutil.which("node")


@unittest.skipUnless(NODE, "画面入力のJavaScriptテストにはNode.jsが必要です。")
class ReturnCaseInputTests(unittest.TestCase):
    def test_only_ascii_digits_enable_return_actions(self):
        scenario = r"""
state.return.loans = [{loan_id:1,size:'1.000'}];
state.return.selectedLoanId = 1;
for (const [value, valid] of [['1',true],['12',true],['99',true],[' 2 ',true],['F8',false],['F-8',false],['AB',false],['１',false],['１２',false],['123',false],['',false]]) {
  state.return.caseNo = value;
  assert.equal(hasReturnCaseNo(),valid,value);
  assert.equal(getReturnCaseNoError()==='',valid,value);
  const html = renderReturnScreen();
  assert(html.includes('inputmode="numeric"'));
  assert(html.includes('pattern="[0-9]{1,2}"'));
  assert.equal(/data-action="return-one"\s+disabled/.test(html),!valid,value);
  assert.equal(/data-action="return-all"\s+disabled/.test(html),!valid,value);
}
state.return.loans = [{loan_id:1,size:'BM20-25W',case_no:'A01',staff_name:'検査担当',machine_code:'A-1',lent_on:'2026-10-12'}];
const html = renderReturnScreen();
assert(html.includes('<th>サイズ</th><th>ケースNo</th><th>担当者</th><th>機番</th><th>貸出日</th>'));
assert(html.includes('<td>BM20-25W</td><td>A01</td><td>検査担当</td><td>A-1</td><td>2026/10/12</td>'));
assert(html.includes('aria-describedby="return-case-note"'));
"""
        result = subprocess.run(
            [NODE, "-"], input="const assert = require('node:assert/strict');\n" + RENDER_SCRIPT + CONTROLLER_SCRIPT + scenario,
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
