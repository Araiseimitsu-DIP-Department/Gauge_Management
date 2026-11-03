"""対象一覧の描画と、領域に応じた列数判定を検証する。"""
import shutil
import subprocess
import unittest

from app.webview.frontend_render import SCRIPT as RENDER_SCRIPT
from app.webview.frontend_controller import SCRIPT as CONTROLLER_SCRIPT
from app.webview.operation_table_layout import SCRIPT as OPERATION_TABLE_LAYOUT_SCRIPT

NODE = shutil.which("node")


@unittest.skipUnless(NODE, "二列表示のJavaScriptテストにはNode.jsが必要です。")
class OperationTableTests(unittest.TestCase):
    def run_script(self, scenario):
        result = subprocess.run(
            [NODE, "-"],
            input="const assert = require('node:assert/strict');\n" + RENDER_SCRIPT + CONTROLLER_SCRIPT + OPERATION_TABLE_LAYOUT_SCRIPT + scenario,
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_rows_keep_original_indices_and_order(self):
        self.run_script(r"""
for (const count of [0, 1, 12, 13, 20, 25, 30, 60]) {
  const rows = Array.from({length:count}, (_,i)=>({loan_id:1000+i, size:String(i)}));
  const html = renderTable(rows, ['サイズ'], row=>[row.size], null, row=>row.loan_id);
  const indices = [...html.matchAll(/data-row-index="(\d+)"/g)].map(x=>Number(x[1]));
  assert.deepEqual(indices, Array.from({length:count},(_,i)=>i));
  assert.equal((html.match(/<table>/g)||[]).length, count===0?0:1);
}
""")

    def test_operations_split_only_when_height_overflows_and_width_allows(self):
        self.run_script(r"""
assert.equal(operationTableNeedsSplit(16, 595, 600, 900), false);
assert.equal(operationTableNeedsSplit(16, 595, 595, 900), false);
assert.equal(operationTableNeedsSplit(16, 595.1, 595, 900), true);
assert.equal(operationTableNeedsSplit(16, 595, 500, 815), false);
assert.equal(operationTableNeedsSplit(16, 595, 500, 816), true);
assert.equal(operationTableNeedsSplit(60, 2135, 2200, 1200), false);
assert.equal(operationTableNeedsSplit(2, 105, 100, 900), true);
assert.equal(operationTableNeedsSplit(1, 105, 100, 900), false);
assert.equal(operationTableNeedsSplit(16, 595, 0, 900), false);
assert.equal(operationTableNeedsSplit(25, 650, 450, 895, 896), false);
assert.equal(operationTableNeedsSplit(25, 650, 450, 896, 896), true);
assert.equal(operationTableColumnCount(36, 900, 400, 600, 360, 180, 3), 3);
assert.equal(operationTableColumnCount(36, 900, 500, 600, 360, 180, 3), 2);
assert.equal(operationTableColumnCount(36, 900, 400, 500, 360, 180, 3), 2);
assert.equal(operationTableColumnCount(36, 900, 200, 1200, 360, 180, 2), 2);
assert.deepEqual(operationTableColumnSizes(25, 2), [13, 12]);
assert.deepEqual(operationTableColumnSizes(36, 3), [12, 12, 12]);
assert.deepEqual(operationTableColumnSizes(10, 3), [4, 3, 3]);
assert.deepEqual(operationTableColumnSizes(2, 3), [1, 1]);
""")

    def test_selection_uses_original_id_for_both_screens(self):
        self.run_script(r"""
const rows = Array.from({length:25}, (_,i)=>({loan_id:1000+i, size:String(i)}));
renderApp = () => {};
state.currentScreen = 'confirmation';
state.confirmation.detailLoans = rows;
for (const index of [0,12,13,24]) {
  selectRowFromCurrentScreen(index);
  const selected = state.confirmation.selectedLoanId;
  assert.equal(selected,1000+index);
  const html = renderTable(rows,['サイズ'],row=>[row.size],selected,row=>row.loan_id);
  assert.equal((html.match(/class="selected"/g)||[]).length,1);
  assert(html.includes(`data-row-index="${index}" class="selected"`));
}
state.currentScreen = 'return';
state.return.loans = [
  {loan_id:1,size:'1.000'},
  {loan_id:2,size:'2.000'},
  {loan_id:3,size:'3.000'},
];
state.return.selectedLoanIds = [];
selectRowFromCurrentScreen(0);
selectRowFromCurrentScreen(2);
assert.deepEqual(state.return.selectedLoanIds,[1,3]);
let html = renderReturnScreen();
assert.equal((html.match(/class="selected"/g)||[]).length,2);
assert(html.includes('個別返却 2件'));
assert(html.includes('>1.000</span>'));
assert(html.includes('>3.000</span>'));
selectRowFromCurrentScreen(0);
assert.deepEqual(state.return.selectedLoanIds,[3]);
html = renderReturnScreen();
assert.equal((html.match(/class="selected"/g)||[]).length,1);
assert(html.includes('個別返却 1件'));
assert(html.includes('>3.000</span>'));
assert(!html.includes('>1.000</span>'));
""")

    def test_row_callbacks_receive_original_index_and_values_are_escaped(self):
        self.run_script(r"""
const rows = Array.from({length:13},(_,i)=>({size:'<サイズ&>',loan_id:1000+i}));
const mapped = [], extracted = [];
const html = renderTable(rows,['<見出し>'],(row,index)=>{mapped.push(index);return [row.size];},1012,(row,index)=>{extracted.push(index);return row.loan_id;});
assert.deepEqual(mapped,Array.from({length:13},(_,i)=>i));
assert.deepEqual(extracted,mapped);
assert(html.includes('&lt;サイズ&amp;&gt;'));
assert(html.includes('&lt;見出し&gt;'));
assert(!html.includes('<サイズ&>'));
""")


if __name__ == "__main__":
    unittest.main()
