"""確認対象一覧を実際の表示領域に合わせて一列・二列に切り替える。"""

SCRIPT = r"""
    let confirmationTableObserver = null;

    function confirmationTableNeedsSplit(rowCount, tableHeight, availableHeight, availableWidth) {
      const MIN_SPLIT_WIDTH = 816;
      return rowCount > 1 && availableHeight > 0 && availableWidth >= MIN_SPLIT_WIDTH
        && Math.ceil(tableHeight) > availableHeight;
    }

    function observeConfirmationTable() {
      if (confirmationTableObserver) confirmationTableObserver.disconnect();
      const wrap = document.querySelector('.confirmation-targets');
      if (!wrap) return;
      if (!confirmationTableObserver) {
        confirmationTableObserver = new ResizeObserver((entries) => {
          for (const entry of entries) layoutConfirmationTable(entry.target);
        });
      }
      layoutConfirmationTable(wrap);
      confirmationTableObserver.observe(wrap);
    }

    function layoutConfirmationTable(wrap) {
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
      const split = confirmationTableNeedsSplit(rows.length, singleTableHeight, wrap.clientHeight, wrap.clientWidth);
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
