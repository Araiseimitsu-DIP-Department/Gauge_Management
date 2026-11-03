"""PG表との左右比較に対応した返却画面の配置。"""

RETURN_STYLES = r"""
    body.return-active .shell { height: 100vh; min-height: 0; overflow: hidden; }
    body.return-active .main { height: 100vh; overflow: auto; }
    body.return-active .main-shell { height: 100%; min-height: 0; }
    .return-screen { min-height: 0; }
    .return-screen .return-layout {
      display: grid; grid-template-rows: auto minmax(0, 1fr); min-height: 0; height: 100%; gap: 10px;
    }
    .return-screen .card-inner { padding: 10px 12px; }
    .return-screen .card-head { padding-bottom: 8px; border-bottom: 1px solid var(--color-border-subtle); }
    .return-screen .return-search-row {
      grid-template-columns: max-content max-content; justify-content: start; align-items: end; gap: 12px;
    }
    .return-screen .return-list-toolbar {
      display: flex; flex-direction: column; align-items: stretch;
      gap: 6px; margin-bottom: 4px; padding: 8px; min-width: 0; max-width: 100%;
      border: 1px solid var(--color-border-subtle); border-radius: 10px;
      background: var(--color-surface-secondary);
    }
    .return-screen .return-input-row {
      display: flex; flex-wrap: wrap; align-items: end; justify-content: flex-start; gap: 8px; min-width: 0;
    }
    .return-screen .return-date-field { flex: 0 0 9.75rem; width: 9.75rem; max-width: none; }
    .return-screen .return-case-field { flex: 0 0 7.5rem; width: 7.5rem; max-width: none; }
    .return-screen .return-date-field .field-label,
    .return-screen .return-case-field .field-label { white-space: nowrap; }
    .return-screen .return-input-row input { width: 100%; min-width: 0; }
    .return-screen .return-input-row > .return-actions {
      flex: 1 0 auto; display: flex; justify-content: flex-end; flex-wrap: nowrap; margin-left: auto;
    }
    .return-screen .return-selection { display: grid; gap: 4px; min-width: 0; }
    .return-screen .return-selection-head {
      display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; min-width: 0;
    }
    .return-screen .return-selection-count { font-size: 12px; font-weight: 500; color: var(--color-text-secondary); white-space: nowrap; }
    .return-screen .return-selection-count.is-selected { font-weight: 700; color: var(--color-text); }
    .return-screen .return-selection-note { font-size: 12px; line-height: 1.4; color: var(--color-text-secondary); }
    .return-screen .return-selection-items { display: flex; flex-wrap: wrap; gap: 4px; }
    .return-screen .return-selection-chip {
      display: inline-flex; align-items: baseline; gap: 6px; margin: 0; padding: 2px 8px; min-height: 24px;
      border-radius: 999px; border: 1px solid var(--color-accent); background: var(--color-accent-soft);
      color: var(--color-text); font-size: 13px; font-weight: 700; line-height: 1.4; cursor: pointer;
    }
    .return-screen .return-selection-chip .case { font-size: 12px; font-weight: 500; color: var(--color-text-secondary); }
    .return-screen .return-selection-chip .remove { font-weight: 700; color: var(--color-text-secondary); }
    .return-screen .return-case-note:not(:empty) {
      min-height: 0; font-size: 11px; line-height: 1.4; margin: 2px 0 4px;
      white-space: normal; overflow: visible; text-overflow: clip;
    }
    .return-screen .return-case-field input { background: var(--color-surface); }
    .return-screen .field-label { font-size: 12px; }
    .return-screen .field-control, .return-screen .btn { min-height: 30px; }
    .return-screen .return-actions { gap: 6px; justify-content: flex-start; }
    .return-screen .return-input-row .return-actions { justify-content: flex-end; }
    .return-screen .return-input-row .return-actions .btn { min-width: 0; padding: 4px 10px; white-space: nowrap; }
    .return-targets tr.selected td { background: var(--color-accent-soft); }
    .return-targets tr.selected td:first-child::before {
      content: "✓"; display: inline-block; margin-right: 4px; color: var(--color-accent-hover); font-weight: 800;
    }
    body.return-active .return-layout .return-targets {
      position: relative; flex: 1 1 0; min-height: 80px; height: auto; max-height: none;
    }
    .return-targets {
      --operation-min-split-width: 360px;
      --operation-column-min-width: 180px;
      --operation-max-columns: 3;
    }
    .return-targets table { min-width: 168px; }
    .return-targets > table { width: min(100%, 280px); }
    .return-targets .split-table-grid { max-width: none; gap: 8px; }
    .return-targets .table-segment + .table-segment { border: 0; }
    .return-targets th:nth-child(1), .return-targets td:nth-child(1) { width: 62%; }
    .return-targets th:nth-child(2), .return-targets td:nth-child(2) { width: 38%; }
    .return-targets tbody td { white-space: nowrap; }
    .return-targets tbody td:nth-child(2) { color: var(--color-text-secondary); font-weight: 500; }
    @media (min-width: 1200px) {
      body.return-active .main-shell {
        width: calc(50vw - var(--sidebar-width) - 10px);
        max-width: calc(50vw - var(--sidebar-width) - 10px);
        margin-left: 0;
        margin-right: auto;
      }
    }
    @media (max-width: 1150px) {
      body.return-active .sidebar .brand { justify-content: center; }
      body.return-active .sidebar-toggle[hidden] { display: none; }
      .return-search-row .field-row { flex-wrap: wrap; }
      .return-search-row .mini-readout { display: none; }
    }
    @media (max-height: 560px) {
      body.return-active .shell { height: auto; min-height: 100vh; overflow: visible; }
      body.return-active .main { height: auto; overflow: visible; }
      body.return-active .main-shell { height: auto; }
      .return-screen .return-layout { grid-template-rows: auto auto; }
      body.return-active .return-layout .return-targets { flex: auto; height: 300px; }
    }
"""
