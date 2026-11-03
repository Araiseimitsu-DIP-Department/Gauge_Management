"""返却・確認の対象一覧を、高さと幅に合わせて1～3列へ切り替える。"""

SCRIPT = r"""
    const DEFAULT_MIN_SPLIT_WIDTH = 816;
    let operationTableObserver = null;

    function operationTableColumnCount(rowCount, tableHeight, availableHeight, availableWidth, minimumSplitWidth = DEFAULT_MIN_SPLIT_WIDTH, columnMinWidth = 0, maxColumns = 2) {
      if (rowCount <= 1 || availableHeight <= 0 || tableHeight <= 0) return 1;
      const rowHeight = tableHeight / rowCount;
      const limit = Math.min(Math.max(1, maxColumns), rowCount);
      let columns = 1;
      for (let count = 2; count <= limit; count += 1) {
        const neededWidth = count === 2 ? minimumSplitWidth : columnMinWidth * count;
        if (availableWidth < neededWidth) break;
        const previousRows = Math.ceil(rowCount / (count - 1));
        if (Math.ceil(rowHeight * previousRows) <= availableHeight) break;
        columns = count;
      }
      return columns;
    }

    function operationTableColumnSizes(rowCount, columnCount) {
      const count = Math.max(1, Math.min(columnCount, Math.max(rowCount, 1)));
      const base = Math.floor(rowCount / count);
      const extra = rowCount % count;
      return Array.from({ length: count }, (_, index) => base + (index < extra ? 1 : 0));
    }

    function operationTableNeedsSplit(rowCount, tableHeight, availableHeight, availableWidth, minimumSplitWidth = DEFAULT_MIN_SPLIT_WIDTH) {
      return operationTableColumnCount(rowCount, tableHeight, availableHeight, availableWidth, minimumSplitWidth) >= 2;
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
        // 複数列の表示中も、1列に戻した場合の高さで判定する。
        const probe = table.cloneNode(true);
        probe.querySelector('tbody').replaceChildren(...rows.map(row => row.cloneNode(true)));
        probe.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none;';
        wrap.append(probe);
        singleTableHeight = probe.getBoundingClientRect().height;
        probe.remove();
      }
      const style = getComputedStyle(wrap);
      const minimumSplitWidth = parseFloat(style.getPropertyValue('--operation-min-split-width')) || DEFAULT_MIN_SPLIT_WIDTH;
      const columnMinWidth = parseFloat(style.getPropertyValue('--operation-column-min-width')) || 0;
      const maxColumns = parseInt(style.getPropertyValue('--operation-max-columns'), 10) || 2;
      const columnCount = operationTableColumnCount(
        rows.length, singleTableHeight, wrap.clientHeight, wrap.clientWidth,
        minimumSplitWidth, columnMinWidth, maxColumns
      );
      const currentColumns = grid ? grid.children.length : 1;
      if (columnCount === currentColumns) return;
      const scrollTop = wrap.scrollTop;
      if (columnCount === 1) {
        table.querySelector('tbody').replaceChildren(...rows);
        wrap.replaceChildren(table);
      } else {
        const sizes = operationTableColumnSizes(rows.length, columnCount);
        const columns = document.createElement('div');
        columns.className = 'split-table-grid';
        columns.style.gridTemplateColumns = `repeat(${sizes.length}, minmax(0, 1fr))`;
        let cursor = 0;
        for (const [index, size] of sizes.entries()) {
          const columnTable = index === 0 ? table : table.cloneNode(true);
          columnTable.querySelector('tbody').replaceChildren(...rows.slice(cursor, cursor + size));
          const segment = document.createElement('div');
          segment.className = 'table-segment';
          const first = cursor + 1;
          const last = cursor + size;
          segment.setAttribute('aria-label', `${first}～${last}件目`);
          segment.append(columnTable);
          columns.append(segment);
          cursor += size;
        }
        wrap.replaceChildren(columns);
      }
      wrap.scrollTop = scrollTop;
    }
"""
