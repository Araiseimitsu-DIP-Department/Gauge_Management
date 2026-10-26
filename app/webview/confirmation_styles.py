"""確認画面の操作エリアと、幅に応じて整列する一覧。"""

CONFIRMATION_STYLES = r"""
    .confirmation-screen {
      --confirmation-font-size: clamp(14px, 0.8vw, 16px);
      --confirmation-single-table-width: 540px;
    }
    .confirmation-screen .two-col {
      grid-template-columns: minmax(0, 1fr) clamp(230px, 17vw, 270px);
      gap: 14px;
    }
    .confirmation-screen .card-inner { padding: clamp(12px, 1vw, 20px); }
    .confirmation-workspace { container: confirmation-workspace / inline-size; }
    .confirmation-screen .card-head {
      min-height: 34px; margin-bottom: 14px; padding-bottom: 12px;
      border-bottom: 1px solid var(--color-border-subtle); gap: 8px;
    }
    .confirmation-screen .card-head h3 { font-size: clamp(15px, 0.9vw, 18px); letter-spacing: 0.02em; }
    .confirmation-screen .card:last-child .card-head { flex-wrap: wrap; }
    .confirmation-screen .metric-pill { font-size: 12px; padding: 4px 10px; }
    .confirmation-toolbar {
      display: grid; grid-template-columns: minmax(220px, 360px) minmax(320px, 1fr);
      align-items: end; gap: 24px; padding: 12px;
      background: var(--color-surface-secondary);
      border: 1px solid var(--color-border-subtle); border-radius: 10px;
      margin-bottom: 8px;
    }
    .confirmation-search-row {
      display: grid; grid-template-columns: minmax(0, 1fr) auto;
      align-items: end; gap: 8px;
    }
    .confirmation-action-row {
      display: grid; grid-template-columns: minmax(110px, 180px) auto;
      align-items: end; justify-content: end; gap: 14px;
    }
    .confirmation-search-row, .confirmation-action-row { margin: 0; }
    .confirmation-search-row .field-group { gap: 0; }
    .confirmation-screen .field-label { font-size: 12px; font-weight: 500; margin-bottom: 5px; }
    .confirmation-screen .field-control, .confirmation-screen .return-selected-size .value,
    .confirmation-screen .btn {
      min-height: 36px; height: auto; font-size: var(--confirmation-font-size);
    }
    .confirmation-screen .field-control { background: var(--color-surface); }
    .confirmation-screen .return-selected-size { gap: 0; }
    .confirmation-screen .return-selected-size .value {
      background: var(--color-surface); border-color: var(--color-border);
      font-weight: 700; font-variant-numeric: tabular-nums;
    }
    .confirmation-screen .return-actions { gap: 8px; }
    .confirmation-screen .btn { padding: 6px 12px; }
    .confirmation-screen .table-wrap {
      border: 0; border-radius: 0; background: transparent;
      scrollbar-gutter: stable;
    }
    .confirmation-screen .table-wrap table {
      font-size: var(--confirmation-font-size); border-collapse: separate; border-spacing: 0;
      table-layout: fixed;
    }
    .confirmation-screen .table-wrap th, .confirmation-screen .table-wrap td {
      padding: 7px 9px; line-height: 20px;
    }
    .confirmation-screen .table-wrap th {
      font-size: 0.86em; font-weight: 600; color: var(--color-text-secondary);
      background: var(--color-surface-secondary);
      border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border);
    }
    .confirmation-screen .table-wrap th:first-child { border-radius: 8px 0 0 0; }
    .confirmation-screen .table-wrap th:last-child { border-radius: 0 8px 0 0; }
    .confirmation-screen .table-wrap tbody tr:nth-child(even):not(.selected) {
      background: color-mix(in srgb, var(--color-surface-secondary) 48%, transparent);
    }
    .confirmation-screen .table-wrap tbody tr:hover:not(.selected) { background: var(--color-accent-soft); }
    .confirmation-screen .table-wrap td { border-bottom-color: var(--color-border-subtle); }
    .confirmation-screen .table-wrap tr.selected td { background: var(--color-accent-soft); font-weight: 600; }
    .confirmation-screen .table-wrap tr.selected td:first-child { box-shadow: inset 3px 0 var(--color-accent); }
    .confirmation-targets { position: relative; }
    .confirmation-targets table { min-width: 370px; }
    .confirmation-targets > table { width: min(100%, var(--confirmation-single-table-width)); }
    .confirmation-targets .split-table-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
    .confirmation-targets .table-segment + .table-segment { border: 0; }
    .confirmation-targets th:nth-child(1) { width: 18%; }
    .confirmation-targets th:nth-child(2) { width: 18%; }
    .confirmation-targets th:nth-child(3) { width: 20%; }
    .confirmation-targets th:nth-child(4) { width: 26%; }
    .confirmation-targets th:nth-child(5) { width: 18%; }
    .confirmation-targets tbody td:first-child { font-weight: 700; }
    .confirmation-targets tbody td:nth-child(2) { color: var(--color-text-secondary); }
    .confirmation-targets tbody td:nth-child(2), .confirmation-targets tbody td:nth-child(3) {
      white-space: normal; overflow-wrap: anywhere;
    }
    .confirmation-targets tbody td:last-child { font-size: 0.9em; }
    .confirmation-batches .table-wrap th:first-child { width: 48%; }
    @container confirmation-workspace (max-width: 740px) {
      .confirmation-toolbar { grid-template-columns: minmax(0, 1fr); gap: 12px; }
      .confirmation-search-row { max-width: 400px; }
      .confirmation-action-row { grid-template-columns: minmax(110px, 180px) auto; justify-content: space-between; }
    }
    @media (max-width: 900px), (max-height: 560px) {
      .confirmation-screen .two-col { grid-template-columns: minmax(0, 1fr); }
    }
    @media (max-width: 640px) {
      .confirmation-action-row { grid-template-columns: minmax(0, 1fr); }
      .confirmation-action-row .return-actions { justify-content: flex-start; flex-wrap: wrap; }
    }
"""
