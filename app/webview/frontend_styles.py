STYLES = r"""
    :root {
      --color-surface: #ffffff;
      --color-surface-secondary: #f4f8fc;
      --color-surface-tertiary: #e9f1f9;
      --color-border: #dce5ee;
      --color-border-subtle: #eef3f8;
      --color-text: #2b2f36;
      --color-text-secondary: #646b75;
      --color-text-tertiary: #9aa3ad;
      --color-accent: #1e88e5;
      --color-accent-hover: #005cac;
      --color-accent-soft: rgba(30, 136, 229, 0.10);
      --color-accent-ring: rgba(30, 136, 229, 0.25);
      --color-success: #10b981;
      --color-success-soft: rgba(16, 185, 129, 0.10);
      --color-danger: #ef4444;
      --color-danger-soft: rgba(239, 68, 68, 0.10);
      --color-warning: #f59e0b;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Hiragino Sans", "Yu Gothic Medium", "Yu Gothic", Meiryo, "Noto Sans JP", sans-serif;
      --radius-lg: 0.5rem;
      --radius-xl: 0.75rem;
      --sidebar-width: 15rem;
      --content-width: 96rem;
    }

    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      background: var(--color-surface-secondary);
      font-family: var(--font-sans);
      color: var(--color-text);
    }
    #app { min-height: 100%; }
    button, input, select { font: inherit; }
    button {
      border: 1px solid transparent;
      border-radius: var(--radius-lg);
      cursor: pointer;
      transition: background-color 0.12s ease, border-color 0.12s ease, color 0.12s ease, box-shadow 0.12s ease;
    }
    button:disabled, input:disabled, select:disabled { opacity: 0.6; cursor: not-allowed; }
    button:focus-visible, input:focus-visible, select:focus-visible {
      outline: none;
      box-shadow: 0 0 0 3px var(--color-accent-ring);
    }
    .shell {
      display: grid;
      grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      width: var(--sidebar-width);
      padding: 1.25rem 1rem 1rem;
      background: var(--color-surface);
      border-right: 1px solid var(--color-border);
      transition: width 0.2s ease, padding 0.2s ease;
    }
    .sidebar.collapsed {
      width: 4rem;
      padding-left: 0.75rem;
      padding-right: 0.75rem;
    }
    .brand {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.5rem;
      padding: 0.25rem 0.25rem 0.75rem;
      border-bottom: 1px solid var(--color-border-subtle);
    }
    .brand-main {
      min-width: 0;
      display: grid;
      gap: 0.5rem;
    }
    .brand-logo {
      display: block;
      max-width: 10.5rem;
      width: 100%;
      height: auto;
    }
    .brand-mark {
      display: none;
      width: 2rem;
      height: 2rem;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-lg);
      background: var(--color-accent-soft);
      color: var(--color-accent);
      font-size: 0.875rem;
      font-weight: 700;
    }
    .brand-caption {
      color: var(--color-text-secondary);
      font-size: 0.75rem;
      font-weight: 500;
      line-height: 1.5;
    }
    .sidebar-toggle {
      width: 2rem;
      height: 2rem;
      min-width: 2rem;
      min-height: 2rem;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: var(--color-surface-secondary);
      border-color: var(--color-border);
      color: var(--color-text-secondary);
      flex: 0 0 auto;
    }
    .sidebar-toggle:hover:not(:disabled) {
      background: var(--color-surface-tertiary);
      color: var(--color-text);
    }
    .nav-group { display: grid; gap: 0.375rem; }
    .nav-btn, .nav-sub-btn, .nav-group-btn {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 0.625rem;
      text-align: left;
      background: transparent;
      padding: 0.625rem 0.75rem;
      color: var(--color-text-secondary);
      font-size: 0.875rem;
      font-weight: 500;
      border: 1px solid transparent;
      border-radius: var(--radius-lg);
    }
    .nav-btn.active, .nav-sub-btn.active, .nav-group-btn.active {
      color: var(--color-text);
      background: var(--color-accent-soft);
      border-color: transparent;
    }
    .nav-btn:hover, .nav-sub-btn:hover, .nav-group-btn:hover {
      background: var(--color-surface-secondary);
    }
    .nav-group-btn { margin-top: 0.375rem; font-weight: 600; }
    .nav-sub-list {
      padding-left: 0.625rem;
      margin-top: 0.125rem;
      display: grid;
      gap: 0.25rem;
      border-left: 1px solid var(--color-border-subtle);
    }
    .nav-sub-btn { padding-left: 0.75rem; font-size: 0.8125rem; }
    .nav-icon {
      width: 1.125rem;
      height: 1.125rem;
      color: currentColor;
      flex: 0 0 auto;
    }
    .nav-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .sidebar.collapsed .brand-logo,
    .sidebar.collapsed .brand-caption,
    .sidebar.collapsed .nav-label,
    .sidebar.collapsed .nav-sub-list {
      display: none;
    }
    .sidebar.collapsed .brand-mark {
      display: inline-flex;
    }
    .sidebar.collapsed .brand {
      justify-content: center;
      padding-left: 0;
      padding-right: 0;
    }
    .sidebar.collapsed .nav-btn,
    .sidebar.collapsed .nav-group-btn {
      justify-content: center;
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }
    .sidebar.collapsed .nav-group {
      justify-items: center;
    }
    .sidebar-footer {
      margin-top: auto;
      padding: 0.875rem 0.875rem 0.25rem;
      border-top: 1px solid var(--color-border-subtle);
      color: var(--color-text-tertiary);
      font-size: 0.75rem;
      line-height: 1.6;
    }
    .sidebar.collapsed .sidebar-footer {
      display: none;
    }
    .main {
      min-width: 0;
      padding: 1.5rem;
    }
    .main-shell {
      min-height: calc(100vh - 3rem);
      max-width: var(--content-width);
      margin: 0 auto;
      display: flex;
      flex-direction: column;
    }
    .screen {
      display: grid;
      gap: 1.25rem;
      flex: 1 1 auto;
    }
    .card {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-xl);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
      overflow: visible;
    }
    .card-inner { padding: 1.5rem; }
    .two-col {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
      gap: 1.25rem;
      align-items: start;
    }
    .two-col.equal { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .lending-layout {
      grid-template-columns: minmax(560px, 1.25fr) minmax(360px, 0.75fr);
      gap: 1rem;
    }
    .lending-layout .card-inner { padding: 1rem 1.125rem; }
    .lending-layout .field-group.inline {
      grid-template-columns: 96px minmax(0, 1fr);
      margin-bottom: 0.5rem;
    }
    .lending-layout .field-row { gap: 0.5rem; margin-bottom: 0.5rem; }
    .lending-layout .button-row { margin-top: 0.25rem; }
    .lending-layout .help {
      margin-top: 0.5rem;
      padding: 0.5rem 0.75rem;
      line-height: 1.45;
    }
    .lending-size-section { margin-top: 0.75rem; }
    .lending-layout .size-grid {
      grid-auto-flow: column;
      grid-template-columns: repeat(3, minmax(160px, 1fr));
      grid-template-rows: repeat(10, minmax(0, auto));
      gap: 8px 12px;
    }
    .lending-layout .size-row {
      grid-template-columns: 24px minmax(0, 1fr);
      gap: 6px;
    }
    .lending-layout .size-index { font-size: 0.8125rem; }
    .lending-layout .field-control.compact {
      min-height: 32px;
      padding: 0.375rem 0.625rem;
    }
    .lending-layout .mini-readout {
      min-width: 96px;
      min-height: 32px;
      padding: 0.375rem 0.625rem;
    }
    .lending-layout .btn {
      min-height: 34px;
      padding: 0.375rem 0.875rem;
    }
    .lending-layout .table-wrap {
      min-height: 220px;
      height: clamp(220px, calc(100vh - 24rem), 460px);
      max-height: 460px;
    }
    .return-layout {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 1rem;
      min-height: 0;
    }
    .return-layout .card-inner { padding: 1.25rem 1.5rem; }
    body.return-active {
      overflow: hidden;
    }
    body.return-active .shell {
      height: 100vh;
      min-height: 0;
      overflow: hidden;
    }
    body.return-active .main {
      height: 100vh;
      overflow: hidden;
    }
    body.return-active .main-shell {
      height: calc(100vh - 3rem);
      min-height: 0;
    }
    body.return-active .return-screen {
      min-height: 0;
    }
    body.return-active .return-layout {
      height: 100%;
    }
    body.return-active .return-layout > .card {
      min-height: 0;
    }
    body.return-active .return-layout > .card:last-child,
    body.return-active .return-layout > .card:last-child > .card-inner {
      display: flex;
      min-height: 0;
      flex-direction: column;
    }
    body.return-active .return-layout .table-wrap {
      flex: 1 1 auto;
      min-height: 0;
      height: auto;
      max-height: none;
    }
    .return-search-row {
      display: grid;
      grid-template-columns: minmax(280px, 1fr) auto;
      gap: 1rem;
      align-items: end;
    }
    .return-list-toolbar {
      display: grid;
      grid-template-columns: minmax(180px, 220px) 480px minmax(0, 1fr) minmax(150px, 200px) auto;
      gap: 0.875rem;
      align-items: end;
      margin-bottom: 0.875rem;
    }
    .return-case-field {
      min-width: 0;
    }
    .return-case-label-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      min-height: 1.125rem;
    }
    .return-case-note {
      color: var(--color-danger);
      font-size: 0.75rem;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .return-actions {
      display: flex;
      gap: 0.625rem;
      flex-wrap: wrap;
      justify-content: flex-end;
      align-items: end;
    }
    .return-selected-size {
      display: grid;
      gap: 0.25rem;
      min-width: 0;
    }
    .return-selected-size .value {
      min-height: 36px;
      display: flex;
      align-items: center;
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      background: var(--color-surface-secondary);
      color: var(--color-text);
      font-size: 0.9375rem;
      font-weight: 600;
    }
    .return-search-button:focus,
    .return-search-button:focus-visible {
      border-color: var(--color-accent);
      background: var(--color-accent-soft);
      color: var(--color-accent-hover);
      box-shadow: 0 0 0 4px var(--color-accent-ring), 0 0 0 1px var(--color-accent);
    }
    .btn.return-one-action {
      background: var(--color-surface);
      border-color: var(--color-border);
      color: var(--color-text);
    }
    .btn.return-one-action:hover:not(:disabled) {
      background: var(--color-surface-secondary);
      border-color: var(--color-border);
    }
    .btn.return-one-action.ready {
      background: var(--color-success);
      border-color: var(--color-success);
      color: #fff;
    }
    .btn.return-one-action.ready:hover:not(:disabled) {
      background: #059669;
      border-color: #059669;
    }
    .btn.return-all-action {
      background: var(--color-accent);
      border-color: var(--color-accent);
      color: #fff;
    }
    .btn.return-all-action:hover:not(:disabled) {
      background: var(--color-accent-hover);
      border-color: var(--color-accent-hover);
    }
    .return-layout .table-wrap {
      min-height: 320px;
      height: clamp(320px, calc(100vh - 32rem), 540px);
      max-height: 540px;
    }
    .confirmation-action-row {
      display: grid;
      grid-template-columns: minmax(150px, 200px) minmax(0, 1fr) auto;
      gap: 0.875rem;
      align-items: end;
      margin-bottom: 0.875rem;
    }
    .confirmation-search-row {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) 120px;
      gap: 0.875rem;
      align-items: end;
      margin-bottom: 0.875rem;
    }
    .confirmation-action-row .return-actions {
      justify-content: flex-end;
    }
    .card-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 0.875rem;
    }
    .card-head h3 { margin: 0; font-size: 1rem; font-weight: 600; }
    .metric-pill {
      display: inline-flex;
      align-items: center;
      padding: 0.125rem 0.5rem;
      border-radius: var(--radius-lg);
      background: var(--color-accent-soft);
      color: var(--color-accent);
      font-size: 0.75rem;
      font-weight: 500;
    }
    .field-row {
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 0.75rem;
    }
    .field-group { display: grid; gap: 0.375rem; margin-bottom: 0.875rem; }
    .field-group.inline {
      grid-template-columns: 128px minmax(0, 1fr);
      align-items: center;
      gap: 0.75rem;
    }
    .field-label { font-size: 0.75rem; font-weight: 500; color: var(--color-text-secondary); }
    .field-control {
      width: 100%;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      background: var(--color-surface);
      color: var(--color-text);
      min-height: 42px;
      padding: 0.5rem 0.75rem;
      outline: none;
      font-size: 0.875rem;
    }
    .field-control.compact {
      min-height: 36px;
      padding: 0.5rem 0.75rem;
      font-size: 0.875rem;
    }
    .field-control:focus {
      border-color: var(--color-accent);
      box-shadow: 0 0 0 3px var(--color-accent-ring);
    }
    .field-control:disabled {
      background: var(--color-surface-secondary);
      color: var(--color-text-secondary);
    }
    .mini-readout {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 120px;
      padding: 0.5rem 0.75rem;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      background: var(--color-surface-secondary);
      color: var(--color-text-secondary);
      font-size: 0.875rem;
      font-weight: 500;
    }
    .stack { display: grid; gap: 14px; }
    .button-row {
      display: flex;
      gap: 0.625rem;
      flex-wrap: wrap;
      align-items: center;
      margin-top: 0.75rem;
    }
    .btn {
      min-width: 92px;
      min-height: 40px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border-radius: var(--radius-lg);
      font-size: 0.875rem;
      font-weight: 500;
    }
    .btn.primary { background: var(--color-accent); border-color: var(--color-accent); color: #fff; }
    .btn.primary:hover:not(:disabled) { background: var(--color-accent-hover); border-color: var(--color-accent-hover); }
    .btn.secondary { background: var(--color-surface); border-color: var(--color-border); color: var(--color-text); }
    .btn.secondary:hover:not(:disabled) { background: var(--color-surface-secondary); }
    .btn.neutral { background: var(--color-surface-secondary); border-color: var(--color-border); color: var(--color-text-secondary); }
    .btn.ghost { background: transparent; border-color: transparent; color: var(--color-text-secondary); }
    .btn.ghost:hover:not(:disabled) { background: var(--color-surface-secondary); color: var(--color-text); }
    .btn.cancel { background: var(--color-surface-secondary); border-color: var(--color-border); color: var(--color-text-secondary); }
    .btn.danger { background: var(--color-danger); border-color: var(--color-danger); color: #fff; }
    .btn.danger:hover:not(:disabled) { background: #dc2626; border-color: #dc2626; }
    .btn.filter {
      min-width: 0;
      min-height: 34px;
      padding: 0.375rem 0.75rem;
      background: var(--color-surface);
      border-color: var(--color-border);
      color: var(--color-text-secondary);
      font-size: 0.75rem;
      font-weight: 500;
    }
    .btn.filter.active { background: var(--color-accent-soft); border-color: transparent; color: var(--color-accent); }
    .btn.small { min-width: 0; min-height: 34px; padding: 0.375rem 0.75rem; font-size: 0.8125rem; }
    .size-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 22px; }
    .size-row { display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 10px; align-items: center; }
    .size-index { font-weight: 600; color: var(--color-text-secondary); text-align: right; }
    .help {
      margin-top: 8px;
      font-size: 0.75rem;
      color: var(--color-text-secondary);
      line-height: 1.55;
      background: var(--color-surface-secondary);
      border-radius: var(--radius-lg);
      padding: 0.75rem;
    }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 0.875rem;
    }
    .toolbar .search-box { min-width: 240px; flex: 1 1 260px; }
    .search-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: end;
    }
    .table-wrap {
      border: 1px solid var(--color-border);
      border-radius: var(--radius-xl);
      overflow: auto;
      min-height: 260px;
      height: clamp(260px, calc(100vh - 22rem), 570px);
      max-height: 570px;
      background: var(--color-surface);
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    thead th {
      position: sticky; top: 0; z-index: 1;
      background: var(--color-surface-secondary);
      color: var(--color-text-secondary);
      font-size: 0.75rem;
      font-weight: 600;
      text-align: left;
      padding: 0.625rem 1rem;
      border-bottom: 1px solid var(--color-border);
    }
    tbody td {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--color-border-subtle);
      vertical-align: top;
    }
    tbody tr {
      border-left: 4px solid transparent;
    }
    tbody tr:hover {
      background: var(--color-surface-secondary);
    }
    tbody tr.selected {
      background: rgba(30, 136, 229, 0.22);
      border-left-color: var(--color-accent);
      box-shadow: inset 0 0 0 1px rgba(30, 136, 229, 0.30);
      color: #102235;
      font-weight: 600;
    }
    tbody tr.selected:hover {
      background: rgba(30, 136, 229, 0.28);
    }
    .inline-note { font-size: 0.75rem; color: var(--color-text-secondary); }
    .empty-state {
      padding: 1.5rem 0.75rem;
      text-align: center;
      color: var(--color-text-secondary);
      font-size: 0.875rem;
    }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(43, 47, 54, 0.18);
      display: grid;
      place-items: center;
      padding: 20px;
      z-index: 40;
    }
    .modal {
      width: min(860px, 100%);
      max-height: calc(100vh - 40px);
      overflow: auto;
      border-radius: var(--radius-xl);
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      box-shadow: 0 12px 30px rgba(43, 47, 54, 0.12);
    }
    .modal-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .modal-head h3 { margin: 0; font-size: 1rem; font-weight: 600; }
    .modal-close {
      background: transparent;
      color: var(--color-text-secondary);
      font-size: 16px;
      font-weight: 800;
      min-width: 40px;
      min-height: 40px;
    }
    .busy-overlay {
      position: fixed;
      inset: 0;
      z-index: 55;
      background: rgba(244, 248, 252, 0.86);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transition: opacity 0.14s ease, visibility 0s linear 0.14s;
    }
    .busy-overlay.visible {
      opacity: 1;
      visibility: visible;
      pointer-events: auto;
      transition: opacity 0.14s ease;
    }
    .busy-card {
      width: min(480px, 100%);
      background: rgba(255,255,255,0.97);
      border-radius: var(--radius-xl);
      border: 1px solid var(--color-border);
      box-shadow: 0 12px 30px rgba(43, 47, 54, 0.10);
      padding: 22px 24px;
      display: grid;
      gap: 14px;
      text-align: center;
    }
    .dialog-overlay {
      position: fixed;
      inset: 0;
      z-index: 58;
      background: rgba(244, 248, 252, 0.86);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transition: opacity 0.14s ease, visibility 0s linear 0.14s;
    }
    .dialog-overlay.visible {
      opacity: 1;
      visibility: visible;
      pointer-events: auto;
      transition: opacity 0.14s ease;
    }
    .dialog-card {
      width: min(420px, 100%);
      background: rgba(255,255,255,0.98);
      border-radius: var(--radius-xl);
      border: 1px solid var(--color-border);
      box-shadow: 0 12px 30px rgba(43, 47, 54, 0.12);
      padding: 22px 24px 20px;
      display: grid;
      gap: 16px;
    }
    .dialog-head {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .dialog-mark {
      width: 42px;
      height: 42px;
      border-radius: var(--radius-lg);
      display: grid;
      place-items: center;
      background: var(--color-surface-secondary);
      color: var(--color-accent);
      font-size: 20px;
      font-weight: 900;
      flex: 0 0 auto;
    }
    .dialog-mark.confirm { background: var(--color-accent-soft); color: var(--color-accent-hover); }
    .dialog-mark.notice { background: var(--color-surface-secondary); color: var(--color-accent); }
    .dialog-mark.error { background: var(--color-danger-soft); color: var(--color-danger); }
    .dialog-title { margin: 0; font-size: 1rem; font-weight: 600; color: var(--color-text); line-height: 1.35; }
    .dialog-subtitle { margin-top: 2px; font-size: 0.75rem; color: var(--color-text-secondary); }
    .dialog-message { font-size: 0.875rem; line-height: 1.7; color: var(--color-text-secondary); white-space: normal; word-break: break-word; }
    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .spinner {
      width: 44px;
      height: 44px;
      margin: 0 auto;
      border-radius: 50%;
      border: 4px solid var(--color-border);
      border-top-color: var(--color-accent);
      animation: spin 0.9s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .app-footer {
      margin-top: 1.5rem;
      padding-top: 0.875rem;
      border-top: 1px solid var(--color-border-subtle);
      color: var(--color-text-tertiary);
      font-size: 0.75rem;
      text-align: center;
    }
"""
