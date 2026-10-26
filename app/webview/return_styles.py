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
      grid-template-columns: 130px 100px 110px max-content;
      justify-content: start; align-items: end; gap: 8px; margin-bottom: 4px; padding: 10px;
      border: 1px solid var(--color-border-subtle); border-radius: 10px;
      background: var(--color-surface-secondary);
    }
    .return-screen .return-case-note:not(:empty) {
      min-height: 0; font-size: 11px; line-height: 1.4; margin: 2px 0 4px;
      white-space: normal; overflow: visible; text-overflow: clip;
    }
    .return-screen .return-case-field input { background: var(--color-surface); }
    .return-screen .return-selected-size .value { background: var(--color-surface); }
    .return-screen .field-label { font-size: 12px; }
    .return-screen .return-selected-size { gap: 3px; }
    .return-screen .field-control, .return-screen .btn { min-height: 30px; }
    .return-screen .return-actions { gap: 6px; justify-content: flex-start; }
    body.return-active .return-layout .return-targets {
      position: relative; flex: 1 1 0; min-height: 80px; height: auto; max-height: none;
    }
    .return-targets { --operation-min-split-width: 896px; }
    .return-targets table { min-width: 440px; }
    .return-targets > table { width: min(100%, 520px); }
    .return-targets .split-table-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr)); max-width: 1056px; gap: 16px;
    }
    .return-targets .table-segment + .table-segment { border: 0; }
    .return-targets th:nth-child(1) { width: 20%; }
    .return-targets th:nth-child(2) { width: 16%; }
    .return-targets th:nth-child(3) { width: 22%; }
    .return-targets th:nth-child(4) { width: 16%; }
    .return-targets th:nth-child(5) { width: 26%; }
    .return-targets tbody td:nth-child(2) { color: var(--color-text-secondary); }
    .return-targets tbody td:nth-child(2), .return-targets tbody td:nth-child(3) {
      white-space: normal; overflow-wrap: anywhere;
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
