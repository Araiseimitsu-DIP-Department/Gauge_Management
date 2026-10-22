"""低解像度でも入力と一覧を同時に確認できる画面配置。"""

LAYOUT_STYLES = r"""
    :root { --sidebar-width: 11rem; --control-height: 30px; }
    .shell { height: 100vh; min-height: 0; }
    .sidebar { min-height: 0; gap: 10px; padding: 12px 10px; }
    .brand { gap: 4px; padding: 0 0 10px; }
    .brand-logo { max-width: 112px; }
    .sidebar.collapsed .brand { flex-direction: column; align-items: center; gap: 6px; }
    .brand-caption { font-size: 12px; }
    .main, body.return-active .main { height: 100vh; padding: 10px; overflow: auto; }
    .main-shell, body.return-active .main-shell { height: 100%; min-height: 0; }
    .screen { min-height: 0; gap: 10px; }
    .two-col, .two-col.equal { gap: 10px; align-items: stretch; min-height: 0; }
    .two-col { grid-template-columns: minmax(0, 1.4fr) minmax(300px, 0.8fr); }
    .confirmation-screen .two-col { grid-template-columns: minmax(0, 1fr) 210px; }
    .confirmation-screen .two-col > .card:last-child .card-head { flex-wrap: wrap; gap: 4px; }
    .return-screen .table-wrap table, .confirmation-screen .table-wrap table { font-size: 12px; }
    .return-screen .table-wrap th, .confirmation-screen .table-wrap th { font-size: 11px; }
    .return-screen .table-wrap th, .return-screen .table-wrap td,
    .confirmation-screen .table-wrap th, .confirmation-screen .table-wrap td { padding: 3px 6px; line-height: 18px; }
    .return-screen tbody td:first-child,
    .confirmation-screen .two-col > .card:first-child tbody td:first-child { font-weight: 700; }
    .split-table-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; align-items: start; }
    .table-segment { min-width: 0; }
    .table-segment + .table-segment { border-left: 1px solid var(--color-border); }
    .lending-layout { grid-template-columns: minmax(420px, 0.95fr) minmax(0, 1.05fr); }
    .card { min-width: 0; min-height: 0; }
    .two-col > .card > .card-inner,
    .return-layout > .card:last-child > .card-inner {
      display: flex; flex-direction: column; height: 100%; min-height: 0;
    }
    .card-inner, .lending-layout .card-inner, .return-layout .card-inner { padding: 10px 12px; }
    .card-inner > :not(.table-wrap) { flex-shrink: 0; }
    .card-head { margin-bottom: 8px; }
    .card-head h3 { font-size: 15px; }
    .field-group { gap: 3px; margin-bottom: 6px; min-width: 0; }
    .field-group.inline, .lending-layout .field-group.inline { grid-template-columns: 60px minmax(0, 1fr); gap: 6px; margin-bottom: 6px; }
    .field-row, .lending-layout .field-row { gap: 6px; margin-bottom: 6px; }
    .field-control, .field-control.compact, .lending-layout .field-control.compact {
      min-height: var(--control-height); height: var(--control-height); padding: 3px 7px; font-size: 13px;
    }
    .mini-readout, .lending-layout .mini-readout { min-width: 82px; min-height: var(--control-height); padding: 3px 7px; font-size: 13px; }
    .btn, .btn.small, .btn.filter, .lending-layout .btn { min-height: var(--control-height); padding: 4px 10px; font-size: 13px; white-space: nowrap; }
    .btn { min-width: 72px; }
    .button-row, .lending-layout .button-row { margin-top: 4px; gap: 6px; }
    .toolbar { gap: 6px; margin-bottom: 8px; }
    .stack { gap: 4px; }
    .lending-size-section { margin-top: 8px; }
    .lending-layout .size-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 8px; }
    .lending-layout .size-row { grid-template-columns: 18px minmax(0, 1fr); gap: 4px; }
    .lending-layout .size-index { font-size: 12px; }
    .lending-layout .search-box { flex-basis: 180px !important; }
    .table-wrap, .lending-layout .table-wrap, .return-layout .table-wrap,
    body.return-active .return-layout .table-wrap {
      flex: 1 1 0; min-height: 100px; height: auto; max-height: none; margin-top: 8px !important;
    }
    table { font-size: 13px; font-variant-numeric: tabular-nums; }
    thead th, tbody td { padding: 6px 8px; white-space: nowrap; }
    tbody td { vertical-align: middle; }
    .return-layout { gap: 10px; }
    .return-search-row { grid-template-columns: minmax(0, 1fr) auto; gap: 10px; }
    .return-list-toolbar { grid-template-columns: 150px minmax(240px, 1fr) minmax(110px, 150px) auto; gap: 10px; margin-bottom: 4px; }
    .return-list-toolbar > [aria-hidden="true"] { display: none; }
    .return-case-label-row { display: grid; gap: 0; }
    .return-case-note { font-size: 11px; }
    .return-case-note:empty { display: none; }
    .return-actions { flex-wrap: nowrap; gap: 6px; }
    .return-selected-size .value { min-height: var(--control-height); padding: 3px 7px; font-size: 13px; }
    .confirmation-search-row { grid-template-columns: minmax(0, 1fr) 90px; gap: 8px; margin-bottom: 8px; }
    .confirmation-action-row { grid-template-columns: 150px minmax(0, 1fr) auto; gap: 8px; margin-bottom: 4px; }
    .app-footer { flex: 0 0 auto; margin-top: 6px; padding-top: 4px; font-size: 11px; }
    .app-version { color: var(--color-text-secondary); font-weight: 600; }
    .help { padding: 6px 8px; }
    @media (max-height: 740px) {
      :root { --control-height: 28px; }
      .lending-layout .help { display: none; }
      .lending-layout .size-grid { gap: 3px 8px; }
      .nav-btn, .nav-sub-btn, .nav-group-btn { padding-top: 6px; padding-bottom: 6px; }
      .sidebar-footer { padding: 6px 2px; font-size: 11px; }
    }
    @media (max-width: 1150px) and (min-width: 901px) {
      .confirmation-screen .split-table-grid { grid-template-columns: minmax(0, 1fr); }
      .lending-layout { grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr); }
      .lending-layout .field-group.inline { grid-template-columns: 48px minmax(0, 1fr); }
      .lending-layout select[data-field*="Machine"] { width: 76px !important; }
      .lending-layout .mini-readout { min-width: 72px; }
      .return-list-toolbar { grid-template-columns: 145px minmax(0, 1fr); }
      .return-list-toolbar .return-actions { justify-content: flex-end; }
    }
    @media (max-width: 900px), (max-height: 560px) {
      .shell, body.return-active .shell { height: auto; min-height: 100vh; overflow: visible; }
      .main, body.return-active .main { height: auto; overflow: visible; }
      .main-shell, body.return-active .main-shell { height: auto; min-height: calc(100vh - 20px); }
      body.return-active { overflow: auto; }
      .two-col, .two-col.equal, .confirmation-screen .two-col { grid-template-columns: minmax(0, 1fr); }
      .table-wrap, .lending-layout .table-wrap, body.return-active .return-layout .table-wrap { flex: auto; height: 300px; }
      .return-list-toolbar { grid-template-columns: minmax(0, 1fr); }
      .return-search-row { grid-template-columns: minmax(0, 1fr); }
      .split-table-grid { grid-template-columns: minmax(0, 1fr); }
    }
"""
