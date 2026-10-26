"""二列表示でも行の順序・ID・選択対象が維持されることを検証する。"""
import shutil
import subprocess
import unittest

from app.webview.frontend_render import SCRIPT as RENDER_SCRIPT
from app.webview.frontend_controller import SCRIPT as CONTROLLER_SCRIPT
from app.webview.confirmation_layout import SCRIPT as CONFIRMATION_LAYOUT_SCRIPT

NODE = shutil.which("node")


@unittest.skipUnless(NODE, "二列表示のJavaScriptテストにはNode.jsが必要です。")
class OperationTableTests(unittest.TestCase):
    def run_script(self, scenario):
        result = subprocess.run(
            [NODE, "-"],
            input="const assert = require('node:assert/strict');\n" + RENDER_SCRIPT + CONTROLLER_SCRIPT + CONFIRMATION_LAYOUT_SCRIPT + scenario,
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_rows_keep_original_indices_and_order(self):
        self.run_script(r"""
for (const count of [0, 1, 12, 13, 20, 25, 30, 60]) {
  const rows = Array.from({length:count}, (_,i)=>({loan_id:1000+i, size:String(i)}));
  const html = renderOperationTable(rows, ['サイズ'], row=>[row.size], null, row=>row.loan_id);
  const indices = [...html.matchAll(/data-row-index="(\d+)"/g)].map(x=>Number(x[1]));
  assert.deepEqual(indices, Array.from({length:count},(_,i)=>i));
  assert.equal((html.match(/<table>/g)||[]).length, count===0?0:count<=12?1:2);
}
""")

    def test_confirmation_splits_only_when_height_overflows_and_width_allows(self):
        self.run_script(r"""
assert.equal(confirmationTableNeedsSplit(16, 595, 600, 900), false);
assert.equal(confirmationTableNeedsSplit(16, 595, 595, 900), false);
assert.equal(confirmationTableNeedsSplit(16, 595.1, 595, 900), true);
assert.equal(confirmationTableNeedsSplit(16, 595, 500, 815), false);
assert.equal(confirmationTableNeedsSplit(16, 595, 500, 816), true);
assert.equal(confirmationTableNeedsSplit(60, 2135, 2200, 1200), false);
assert.equal(confirmationTableNeedsSplit(2, 105, 100, 900), true);
assert.equal(confirmationTableNeedsSplit(1, 105, 100, 900), false);
assert.equal(confirmationTableNeedsSplit(16, 595, 0, 900), false);
""")

    def test_right_column_selection_uses_original_id_for_both_screens(self):
        self.run_script(r"""
const rows = Array.from({length:25}, (_,i)=>({loan_id:1000+i, size:String(i)}));
renderApp = () => {};
for (const screen of ['return', 'confirmation']) {
  state.currentScreen = screen;
  state.return.loans = rows;
  state.confirmation.detailLoans = rows;
  for (const index of [0,12,13,24]) {
    selectRowFromCurrentScreen(index);
    const selected = state[screen].selectedLoanId;
    assert.equal(selected,1000+index);
    const html = renderOperationTable(rows,['サイズ'],row=>[row.size],selected,row=>row.loan_id);
    assert.equal((html.match(/class="selected"/g)||[]).length,1);
    assert(html.includes(`data-row-index="${index}" class="selected"`));
  }
}
""")

    def test_row_callbacks_receive_original_index_and_values_are_escaped(self):
        self.run_script(r"""
const rows = Array.from({length:13},(_,i)=>({size:'<サイズ&>',loan_id:1000+i}));
const mapped = [], extracted = [];
const html = renderOperationTable(rows,['<見出し>'],(row,index)=>{mapped.push(index);return [row.size];},1012,(row,index)=>{extracted.push(index);return row.loan_id;});
assert.deepEqual(mapped,Array.from({length:13},(_,i)=>i));
assert.deepEqual(extracted,mapped);
assert(html.includes('&lt;サイズ&amp;&gt;'));
assert(html.includes('&lt;見出し&gt;'));
assert(!html.includes('<サイズ&>'));
""")


if __name__ == "__main__":
    unittest.main()
