"""貸出・マスタ管理の入力と一覧を画面幅に応じて配置する。"""

WORKSPACE_STYLES = r"""
    body.workspace-active .shell { height: 100vh; min-height: 0; }
    body.workspace-active .main { height: 100vh; overflow: auto; }
    body.workspace-active .main-shell { height: 100%; min-height: 0; }
    .workspace-screen > .two-col { height: 100%; min-height: 0; }
    .workspace-screen .card-inner { padding: 12px; }
    .workspace-screen .card-head {
      min-height: 28px; gap: 8px; margin-bottom: 10px; padding-bottom: 8px;
      border-bottom: 1px solid var(--color-border-subtle);
    }
    .workspace-screen .card-head h3 { font-size: 15px; white-space: nowrap; }
    .workspace-screen .field-label { font-size: 12px; }
    .workspace-screen .field-control { min-height: 30px; font-size: 13px; }
    .workspace-screen .btn { min-height: 30px; }
    .workspace-screen .table-wrap { flex: 1 1 0; height: auto; min-height: 100px; max-height: none; }
    .workspace-screen .operation-table table { width: 100%; font-size: 13px; }
    .workspace-screen .operation-table th { font-size: 12px; }
    .workspace-screen .operation-table th, .workspace-screen .operation-table td { padding: 4px 8px; line-height: 20px; }
    .workspace-screen .operation-table tbody td:first-child { font-weight: 700; }
    .workspace-screen .operation-table tbody td { white-space: normal; overflow-wrap: anywhere; }
    .workspace-screen .button-row { justify-content: flex-start; gap: 6px; }
    .lending-screen .lending-layout { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .lending-layout > .card:first-child .card-inner { overflow: auto; }
    .lending-screen .field-group.inline { grid-template-columns: 50px minmax(0, 1fr); }
    .lending-screen [data-field="registerDate"] { max-width: 170px; }
    .lending-screen [data-field="registerStaffId"] { max-width: 300px; }
    .lending-screen .lending-layout select[data-field*="Machine"] { width: 76px !important; }
    .lending-screen .mini-readout { min-width: 74px; }
    .lending-screen .size-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 8px; }
    .lending-screen .size-row { grid-template-columns: 18px minmax(0, 1fr); gap: 4px; }
    .lending-screen .lending-size-section .card-head { min-height: 24px; margin-bottom: 6px; padding-bottom: 4px; }
    .lending-screen .lending-layout .help { font-size: 11px; padding: 6px; }
    .lending-screen .toolbar { justify-content: flex-start; flex-wrap: wrap; gap: 14px; }
    .lending-screen .toolbar .card-head { border: 0; padding: 0; }
    .lending-search-panel {
      padding: 10px; background: var(--color-surface-secondary);
      border: 1px solid var(--color-border-subtle); border-radius: 10px;
    }
    .lending-search-panel [hidden] { display: none; }
    .lending-screen .lending-search-panel .search-box { flex: 0 1 210px !important; }
    .lending-search-panel .field-row { margin-bottom: 0; }
    .lending-search-panel .field-group { margin-bottom: 4px; }
    .lending-search-panel .button-row { margin-top: 6px; }
    .lending-screen .lending-list table { min-width: 420px; max-width: 720px; }
    .lending-list th:nth-child(1) { width: 18%; }
    .lending-list th:nth-child(2) { width: 14%; }
    .lending-list th:nth-child(3) { width: 22%; }
    .lending-list th:nth-child(4) { width: 10%; }
    .lending-list th:nth-child(5) { width: 22%; }
    .lending-list th:nth-child(6) { width: 14%; }
    .workspace-screen .master-layout { grid-template-columns: minmax(0, 1fr) 280px; gap: 12px; }
    .master-layout > .card:last-child { align-self: start; }
    .master-layout > .card:last-child > .card-inner { height: auto; }
    .master-list-toolbar { flex-direction: column; align-items: stretch; gap: 8px; }
    .master-list-toolbar .card-head { justify-content: flex-start; }
    .master-search-row {
      display: grid; grid-template-columns: minmax(140px, 240px) max-content;
      justify-content: start; align-items: end; gap: 8px;
    }
    .master-search-row .search-box { min-width: 0; width: auto; }
    .master-search-row .search-actions { display: flex; gap: 6px; }
    .master-edit-fields { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; }
    .master-edit-fields .field-group { margin: 0; }
    .master-layout > .card:last-child .button-row { margin-top: 12px; }
    .workspace-screen .pg-list table { min-width: 300px; max-width: 560px; }
    .pg-list th:nth-child(1) { width: 40%; }
    .pg-list th:nth-child(2) { width: 20%; }
    .pg-list th:nth-child(3) { width: 40%; }
    .workspace-screen .staff-list table { min-width: 430px; max-width: 680px; }
    .staff-list th:nth-child(1) { width: 20%; }
    .staff-list th:nth-child(2) { width: 26%; }
    .staff-list th:nth-child(3) { width: 20%; }
    .staff-list th:nth-child(4) { width: 20%; }
    .staff-list th:nth-child(5) { width: 14%; }
    body.master-active .sidebar.collapsed .nav-sub-list { display: grid; padding: 0; border: 0; }
    body.master-active .sidebar.collapsed .nav-sub-btn { justify-content: center; padding: 8px; }
    @media (max-width: 1150px) {
      body.workspace-active .sidebar .brand { justify-content: center; }
      body.workspace-active .sidebar-toggle[hidden] { display: none; }
    }
    @media (max-width: 1050px) {
      .lending-screen { flex: 0 0 auto; }
      .lending-screen .lending-layout { grid-template-columns: minmax(0, 1fr); height: auto; }
      .lending-screen .lending-layout > .card > .card-inner { height: auto; }
      .lending-screen .lending-list { flex: auto; height: 340px; }
      .workspace-screen .master-layout { grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(220px, 1fr) auto; }
      .pg_master-screen .master-edit-fields { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .staff_master-screen .master-edit-fields { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-height: 560px) {
      .workspace-screen { flex: 0 0 auto; }
      .workspace-screen > .two-col { height: auto; }
      .workspace-screen .table-wrap { flex: auto; height: 300px; }
      .workspace-screen .master-layout { grid-template-rows: auto auto; }
    }
"""
