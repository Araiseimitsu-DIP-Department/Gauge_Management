"""各画面の一覧で共通の見出し、交互背景、選択行。"""

OPERATION_TABLE_STYLES = r"""
    .operation-table { border: 0; border-radius: 0; background: transparent; scrollbar-gutter: stable; }
    .operation-table table { border-collapse: separate; border-spacing: 0; table-layout: fixed; }
    .operation-table thead th {
      font-weight: 600; color: var(--color-text-secondary); background: var(--color-surface-secondary);
      border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border);
    }
    .operation-table th:first-child { border-radius: 8px 0 0 0; }
    .operation-table th:last-child { border-radius: 0 8px 0 0; }
    .operation-table tbody tr:nth-child(even):not(.selected) {
      background: color-mix(in srgb, var(--color-surface-secondary) 48%, transparent);
    }
    .operation-table tbody tr:hover:not(.selected) { background: var(--color-accent-soft); }
    .operation-table tbody td { border-bottom-color: var(--color-border-subtle); }
    .operation-table tr.selected td { background: var(--color-accent-soft); font-weight: 600; }
    .operation-table tr.selected td:first-child { box-shadow: inset 3px 0 var(--color-accent); }
"""
