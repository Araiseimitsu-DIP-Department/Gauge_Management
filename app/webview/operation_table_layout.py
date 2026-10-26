"""返却・確認の対象一覧を実際の表示領域に合わせて一列・二列に切り替える。"""

SCRIPT = r"""
    const DEFAULT_MIN_SPLIT_WIDTH = 816;
    let operationTableObserver = null;

    function operationTableNeedsSplit(rowCount, tableHeight, availableHeight, availableWidth, minimumSplitWidth = DEFAULT_MIN_SPLIT_WIDTH) {
      return rowCount > 1 && availableHeight > 0 && availableWidth >= minimumSplitWidth
        && Math.ceil(tableHeight) > availableHeight;
    }

    function observeOperationTable() {
      if (operationTableObserver) operationTableObserver.disconnect();
      const wrap = document.querySelector('.confirmation-targets, .return-targets');
      if (!wrap) return;
      if (!operationTableObserver) {
        operationTableObserver = new ResizeObserver((entries) => {
          for (const entry of entries) layoutOperationTable(entry.target);
        });
      }
      layoutOperationTable(wrap);
      operationTableObserver.observe(wrap);
    }

    function layoutOperationTable(wrap) {
      const table = wrap.querySelector('table');
      if (!table) return;
      const grid = wrap.querySelector('.split-table-grid');
      const rows = Array.from(wrap.querySelectorAll('tbody tr'));
      let singleTableHeight = table.getBoundingClientRect().height;
      if (grid) {
        // 二列表示中も、一列に戻した場合の高さで判定する。
        const probe = table.cloneNode(true);
        probe.querySelector('tbody').replaceChildren(...rows.map(row => row.cloneNode(true)));
        probe.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none;';
        wrap.append(probe);
        singleTableHeight = probe.getBoundingClientRect().height;
        probe.remove();
      }
      const minimumSplitWidth = parseFloat(getComputedStyle(wrap).getPropertyValue('--operation-min-split-width')) || DEFAULT_MIN_SPLIT_WIDTH;
      const split = operationTableNeedsSplit(rows.length, singleTableHeight, wrap.clientHeight, wrap.clientWidth, minimumSplitWidth);
      if (split === Boolean(grid)) return;
      const scrollTop = wrap.scrollTop;
      if (split) {
        const splitAt = Math.ceil(rows.length / 2);
        const secondTable = table.cloneNode(true);
        secondTable.querySelector('tbody').replaceChildren(...rows.slice(splitAt));
        const columns = document.createElement('div');
        columns.className = 'split-table-grid';
        for (const [index, columnTable] of [table, secondTable].entries()) {
          const segment = document.createElement('div');
          segment.className = 'table-segment';
          const first = index === 0 ? 1 : splitAt + 1;
          const last = index === 0 ? splitAt : rows.length;
          segment.setAttribute('aria-label', `${first}～${last}件目`);
          segment.append(columnTable);
          columns.append(segment);
        }
        wrap.replaceChildren(columns);
      } else {
        table.querySelector('tbody').replaceChildren(...rows);
        wrap.replaceChildren(table);
      }
      wrap.scrollTop = scrollTop;
    }
"""
