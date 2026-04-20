from __future__ import annotations


def build_html(app_name: str) -> str:
    return _HTML.replace("__APP_NAME__", _escape_html(app_name))


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


_HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__APP_NAME__</title>
  <style>
    :root {
      --bg: #f5f7fa;
      --panel: #ffffff;
      --panel-soft: #eef3f8;
      --line: #d6dfe9;
      --text: #18212b;
      --muted: #5f6f81;
      --brand: #0d5ab6;
      --brand-2: #0c4e9a;
      --danger: #a34d58;
      --radius: 18px;
      --shadow: 0 18px 40px rgba(22, 34, 48, 0.08);
    }

    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      background:
        radial-gradient(circle at top left, rgba(13, 90, 182, 0.07), transparent 28%),
        radial-gradient(circle at bottom right, rgba(12, 78, 154, 0.06), transparent 26%),
        var(--bg);
      font-family: "Yu Gothic UI", "Meiryo", "Segoe UI", sans-serif;
      color: var(--text);
    }
    button, input, select { font: inherit; }
    button {
      border: 0;
      border-radius: 12px;
      cursor: pointer;
      transition: transform 0.12s ease, opacity 0.12s ease, background 0.12s ease;
    }
    button:hover { transform: translateY(-1px); }
    button:disabled, input:disabled, select:disabled { opacity: 0.6; cursor: not-allowed; }
    .shell {
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr);
      min-height: 100vh;
    }
    .sidebar {
      padding: 22px 18px 18px;
      background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(241,245,250,0.96));
      border-right: 1px solid rgba(214, 223, 233, 0.8);
    }
    .brand {
      padding: 8px 10px 12px;
      margin-bottom: 18px;
    }
    .brand h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.25;
      font-weight: 800;
      color: var(--brand);
    }
    .nav-group { display: grid; gap: 8px; }
    .nav-btn, .nav-sub-btn, .nav-group-btn {
      width: 100%;
      text-align: left;
      background: transparent;
      padding: 12px 14px 12px 16px;
      color: #304255;
      font-weight: 700;
      border-left: 4px solid transparent;
      border-radius: 12px;
    }
    .nav-btn.active, .nav-sub-btn.active, .nav-group-btn.active {
      color: var(--brand);
      background: rgba(13, 90, 182, 0.05);
      border-left-color: var(--brand);
    }
    .nav-btn:hover, .nav-sub-btn:hover, .nav-group-btn:hover {
      background: rgba(13, 90, 182, 0.07);
    }
    .nav-group-btn { margin-top: 10px; font-weight: 800; }
    .nav-sub-list { padding-left: 8px; margin-top: 6px; display: grid; gap: 6px; }
    .nav-sub-btn { padding-left: 18px; font-size: 14px; color: #405164; }
    .sidebar-footer {
      margin-top: 18px;
      padding: 10px 12px;
      border-radius: 14px;
      background: rgba(255,255,255,0.72);
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
    }
    .main { padding: 24px 26px; min-width: 0; }
    .header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }
    .header h2 {
      margin: 0;
      font-size: 26px;
      line-height: 1.2;
      font-weight: 800;
      color: var(--brand);
    }
    .header p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
      font-weight: 600;
    }
    .card {
      background: var(--panel);
      border: 1px solid rgba(214, 223, 233, 0.85);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: visible;
    }
    .card-inner { padding: 22px 24px; }
    .two-col {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(340px, 0.85fr);
      gap: 18px;
      align-items: start;
    }
    .two-col.equal { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .card-head h3 { margin: 0; font-size: 18px; font-weight: 800; }
    .metric-pill {
      padding: 6px 10px;
      border-radius: 12px;
      background: #eef3f8;
      color: var(--brand);
      font-size: 13px;
      font-weight: 800;
    }
    .field-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 12px;
    }
    .field-group { display: grid; gap: 6px; margin-bottom: 12px; }
    .field-group.inline {
      grid-template-columns: 128px minmax(0, 1fr);
      align-items: center;
      gap: 12px;
    }
    .field-label { font-size: 12px; font-weight: 700; color: #465463; }
    .field-control {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
      color: var(--text);
      min-height: 42px;
      padding: 10px 12px;
      outline: none;
    }
    .field-control.compact {
      min-height: 36px;
      padding: 8px 10px;
      font-size: 13px;
    }
    .field-control:focus {
      border-color: rgba(13, 90, 182, 0.9);
      box-shadow: 0 0 0 3px rgba(13, 90, 182, 0.12);
    }
    .mini-readout {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 120px;
      padding: 8px 12px;
      border-radius: 10px;
      background: #e8edf3;
      color: #1b2430;
      font-size: 13px;
      font-weight: 800;
    }
    .stack { display: grid; gap: 14px; }
    .button-row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      margin-top: 10px;
    }
    .btn {
      min-width: 92px;
      min-height: 40px;
      padding: 10px 16px;
      border-radius: 12px;
      font-weight: 700;
    }
    .btn.primary { background: linear-gradient(135deg, var(--brand-2), #0e6bd1); color: #fff; }
    .btn.secondary { background: #eaf1f8; color: var(--brand); }
    .btn.neutral { background: #f2f4f7; color: #4d5967; }
    .btn.ghost { background: #f4e8ea; color: var(--danger); }
    .btn.filter {
      min-width: 0;
      min-height: 34px;
      padding: 8px 14px;
      border-radius: 14px;
      background: #eceef1;
      color: #4d5560;
      font-size: 12px;
      font-weight: 700;
    }
    .btn.filter.active { background: var(--brand); color: #fff; }
    .btn.small { min-width: 0; min-height: 34px; padding: 8px 12px; font-size: 12px; }
    .size-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px 22px; }
    .size-row { display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 10px; align-items: center; }
    .size-index { font-weight: 800; color: #526273; text-align: right; }
    .help {
      margin-top: 8px;
      font-size: 12px;
      color: #5c7288;
      line-height: 1.55;
      background: #f4f7fb;
      border-radius: 12px;
      padding: 10px 12px;
    }
    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }
    .toolbar .search-box { min-width: 240px; flex: 1 1 260px; }
    .search-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: end;
    }
    .table-wrap {
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: auto;
      max-height: 570px;
      background: #fff;
    }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    thead th {
      position: sticky; top: 0; z-index: 1;
      background: #f3f5f8;
      color: #4c5562;
      font-size: 12px;
      font-weight: 800;
      text-align: left;
      padding: 12px 12px;
      border-bottom: 1px solid #e2e8ef;
    }
    tbody td { padding: 11px 12px; border-bottom: 1px solid #eef1f4; vertical-align: top; }
    tbody tr:hover { background: #f6f9fc; }
    tbody tr.selected { background: #dfeeff; }
    .inline-note { font-size: 12px; color: var(--muted); }
    .empty-state { padding: 24px 12px; text-align: center; color: var(--muted); font-size: 13px; }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(9, 18, 28, 0.42);
      display: grid;
      place-items: center;
      padding: 20px;
      z-index: 40;
    }
    .modal {
      width: min(860px, 100%);
      max-height: calc(100vh - 40px);
      overflow: auto;
      border-radius: 22px;
      background: #fff;
      border: 1px solid rgba(214, 223, 233, 0.85);
      box-shadow: 0 30px 80px rgba(8, 18, 31, 0.26);
    }
    .modal-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }
    .modal-head h3 { margin: 0; font-size: 20px; font-weight: 800; }
    .modal-close { background: transparent; color: var(--muted); font-size: 16px; font-weight: 800; min-width: 40px; min-height: 40px; }
    .busy-overlay {
      position: fixed;
      inset: 0;
      z-index: 55;
      background: rgba(246, 247, 249, 0.72);
      backdrop-filter: blur(6px);
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
      background: rgba(255,255,255,0.95);
      border-radius: 22px;
      border: 1px solid rgba(214, 223, 233, 0.9);
      box-shadow: 0 30px 70px rgba(8, 18, 31, 0.18);
      padding: 22px 24px;
      display: grid;
      gap: 14px;
      text-align: center;
    }
    .dialog-overlay {
      position: fixed;
      inset: 0;
      z-index: 58;
      background: rgba(246, 247, 249, 0.72);
      backdrop-filter: blur(6px);
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
      border-radius: 22px;
      border: 1px solid rgba(214, 223, 233, 0.95);
      box-shadow: 0 30px 70px rgba(8, 18, 31, 0.20);
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
      border-radius: 14px;
      display: grid;
      place-items: center;
      background: #eef3f8;
      color: var(--brand);
      font-size: 20px;
      font-weight: 900;
      flex: 0 0 auto;
    }
    .dialog-mark.confirm { background: #edf4ff; color: var(--brand-2); }
    .dialog-mark.notice { background: #eef3f8; color: var(--brand); }
    .dialog-mark.error { background: #fdecef; color: #b23d4a; }
    .dialog-title { margin: 0; font-size: 18px; font-weight: 800; color: var(--text); line-height: 1.35; }
    .dialog-subtitle { margin-top: 2px; font-size: 12px; color: var(--muted); }
    .dialog-message { font-size: 14px; line-height: 1.7; color: #415161; white-space: normal; word-break: break-word; }
    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .btn.cancel { background: #eef2f6; color: #546272; }
    .spinner {
      width: 44px;
      height: 44px;
      margin: 0 auto;
      border-radius: 50%;
      border: 4px solid #dbe5f1;
      border-top-color: var(--brand);
      animation: spin 0.9s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .screen { animation: none; }
    @media (max-width: 1200px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { border-right: 0; border-bottom: 1px solid rgba(214, 223, 233, 0.8); }
      .two-col, .two-col.equal { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      .main { padding: 18px 14px 20px; }
      .card-inner { padding: 18px 16px; }
      .field-group.inline { grid-template-columns: 1fr; }
      .header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <div id="app"></div>
  <div id="modal-root"></div>
  <div id="dialog-root"></div>
  <div id="busy-root"></div>
  <script>
    const state = {
      appName: "__APP_NAME__",
      currentDate: "",
      screenTitles: {
        lending: { title: "貸出", subtitle: "貸出登録と貸出一覧" },
        return: { title: "返却", subtitle: "返却対象の検索と返却処理" },
        confirmation: { title: "確認", subtitle: "返却済みデータの確認処理" },
        pg_master: { title: "PGマスタ", subtitle: "PGマスタの検索と編集" },
        staff_master: { title: "担当者マスタ", subtitle: "担当者情報の編集" },
      },
      currentScreen: "lending",
      initialErrors: [],
      options: {
        lendingMachinePrefixes: [],
        returnMachinePrefixes: [],
        machineSuffixes: [],
        departments: [],
      },
      numberMachinePrefix: "",
      lending: {
        registerDate: "",
        registerMachinePrefix: "",
        registerMachineSuffix: "",
        registerStaffId: "",
        registerGaugeSizes: Array.from({ length: 20 }, () => ""),
        searchMode: "size",
        searchSizePrefix: "",
        searchMachinePrefix: "",
        searchMachineSuffix: "",
        useSizePrefixMatch: false,
        staffMembers: [],
        loans: [],
        selectedLoanId: null,
      },
      return: {
        date: "",
        machinePrefix: "",
        machineSuffix: "",
        caseNo: "",
        loans: [],
        selectedLoanId: null,
      },
      confirmation: {
        caseNo: "",
        detailLoans: [],
        selectedLoanId: null,
        batches: [],
        selectedBatchMachineCode: "",
      },
      pgMaster: {
        searchQuery: "",
        rows: [],
        selectedSize: "",
        editSize: "",
        editHoldingCount: 0,
        editCaseNo: "",
        isNew: true,
      },
      staffMaster: {
        searchQuery: "",
        rows: [],
        selectedStaffId: "",
        editStaffId: "",
        editName: "",
        editDepartment: "製造",
        editKana: "",
        editVisible: true,
      },
      modal: null,
      busy: null,
      dialog: null,
      loanEditMachinePrefix: "",
      loanEditMachineSuffix: "",
      shellRendered: false,
      __started: false,
    };

    const dialogQueue = [];
    let activeDialog = null;

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function formatDate(value) {
      if (!value) return "";
      const text = String(value).slice(0, 10);
      const parts = text.split("-");
      return parts.length === 3 ? `${parts[0]}/${parts[1]}/${parts[2]}` : text;
    }

    function machineCode(prefix, suffix) {
      const p = String(prefix ?? "").trim();
      const s = String(suffix ?? "").trim();
      if (!p) return "(未入力)";
      if (p === state.numberMachinePrefix) return state.numberMachinePrefix;
      if (!s) return "(未入力)";
      return `${p}-${s}`;
    }

    function splitMachineCode(machineCodeValue) {
      const normalized = String(machineCodeValue ?? "").trim();
      if (!normalized) {
        return { prefix: "", suffix: "" };
      }
      if (normalized === state.numberMachinePrefix) {
        return { prefix: state.numberMachinePrefix, suffix: "" };
      }
      const parts = normalized.split("-", 2);
      if (parts.length === 2) {
        return { prefix: parts[0].trim(), suffix: parts[1].trim() };
      }
      return { prefix: normalized, suffix: "" };
    }

    function rowClasses(selected) {
      return selected ? "selected" : "";
    }

    function renderApp() {
      const title = state.screenTitles[state.currentScreen];
      const app = document.getElementById("app");
      if (!state.shellRendered || !app.firstElementChild) {
        app.innerHTML = `
          <div class="shell">
            <aside class="sidebar">
              <div class="brand">
                <h1>${escapeHtml(state.appName)}</h1>
              </div>
              <div class="nav-group">
                <button class="nav-btn ${state.currentScreen === "lending" ? "active" : ""}" data-action="navigate" data-screen="lending">貸出</button>
                <button class="nav-btn ${state.currentScreen === "return" ? "active" : ""}" data-action="navigate" data-screen="return">返却</button>
                <button class="nav-btn ${state.currentScreen === "confirmation" ? "active" : ""}" data-action="navigate" data-screen="confirmation">確認</button>
              </div>
              <button class="nav-group-btn ${state.currentScreen === "pg_master" || state.currentScreen === "staff_master" ? "active" : ""}" data-action="toggle-master">マスタ管理</button>
              <div class="nav-sub-list" style="display:${state.currentScreen === "pg_master" || state.currentScreen === "staff_master" ? "grid" : "none"}">
                <button class="nav-sub-btn ${state.currentScreen === "pg_master" ? "active" : ""}" data-action="navigate" data-screen="pg_master">PGマスタ</button>
                <button class="nav-sub-btn ${state.currentScreen === "staff_master" ? "active" : ""}" data-action="navigate" data-screen="staff_master">担当者マスタ</button>
              </div>
              <div class="sidebar-footer">
                <div>DB: ${escapeHtml(state.databaseBackend || "")}</div>
                <div>起動日: ${escapeHtml(state.currentDate || "")}</div>
              </div>
            </aside>
            <main class="main">
              <div class="header">
                <div>
                  <h2 id="screen-title">${escapeHtml(title.title)}</h2>
                  <p id="screen-subtitle">${escapeHtml(title.subtitle)}</p>
                </div>
              </div>
              <div class="screen" id="screen-root">${renderCurrentScreen()}</div>
            </main>
          </div>
        `;
        state.shellRendered = true;
      } else {
        const titleNode = document.getElementById("screen-title");
        const subtitleNode = document.getElementById("screen-subtitle");
        const screenRoot = document.getElementById("screen-root");
        const navButtons = Array.from(document.querySelectorAll("[data-action=\"navigate\"]"));
        const masterButton = document.querySelector("[data-action=\"toggle-master\"]");
        const subList = document.querySelector(".nav-sub-list");
        if (titleNode) titleNode.textContent = title.title;
        if (subtitleNode) subtitleNode.textContent = title.subtitle;
        if (screenRoot) screenRoot.innerHTML = renderCurrentScreen();
        for (const button of navButtons) {
          const screen = button.dataset.screen;
          button.classList.toggle("active", screen === state.currentScreen);
        }
        if (masterButton) {
          masterButton.classList.toggle("active", state.currentScreen === "pg_master" || state.currentScreen === "staff_master");
        }
        if (subList) {
          subList.style.display = state.currentScreen === "pg_master" || state.currentScreen === "staff_master" ? "grid" : "none";
        }
      }
      renderModal();
      renderBusy();
    }

    function renderBusy() {
      const root = document.getElementById("busy-root");
      if (!root) return;
      if (!root.firstElementChild) {
        root.innerHTML = `
          <div class="busy-overlay">
            <div class="busy-card">
              <div class="spinner"></div>
              <div class="busy-title" style="font-size:16px;font-weight:800;"></div>
              <div class="busy-message" style="font-size:13px;color:var(--muted);line-height:1.6;"></div>
            </div>
          </div>
        `;
      }
      const overlay = root.firstElementChild;
      const title = overlay.querySelector(".busy-title");
      const message = overlay.querySelector(".busy-message");
      if (title) title.textContent = state.busy ? state.busy.title : "";
      if (message) message.textContent = state.busy ? state.busy.message : "";
      overlay.classList.toggle("visible", !!state.busy);
    }

    function renderModal() {
      const root = document.getElementById("modal-root");
      root.innerHTML = state.modal ? state.modal.html : "";
    }

    function renderDialog() {
      const root = document.getElementById("dialog-root");
      if (!root) return;
      if (!root.firstElementChild) {
        root.innerHTML = `
          <div class="dialog-overlay">
            <div class="dialog-card" data-modal-stop>
              <div class="dialog-head">
                <div class="dialog-mark notice">i</div>
                <div>
                  <div class="dialog-title"></div>
                  <div class="dialog-subtitle"></div>
                </div>
              </div>
              <div class="dialog-message"></div>
              <div class="dialog-actions">
                <button class="btn cancel" data-dialog-action="cancel">キャンセル</button>
                <button class="btn primary" data-dialog-action="confirm">OK</button>
              </div>
            </div>
          </div>
        `;
      }
      const overlay = root.firstElementChild;
      const mark = overlay.querySelector(".dialog-mark");
      const title = overlay.querySelector(".dialog-title");
      const subtitle = overlay.querySelector(".dialog-subtitle");
      const message = overlay.querySelector(".dialog-message");
      const cancelButton = overlay.querySelector('[data-dialog-action="cancel"]');
      if (!activeDialog) {
        overlay.classList.remove("visible");
        return;
      }
      const dialog = activeDialog;
      const isConfirm = dialog.kind === "confirm";
      if (mark) {
        mark.className = `dialog-mark ${escapeHtml(dialog.kind || "notice")}`;
        mark.textContent = dialog.kind === "confirm" ? "?" : dialog.kind === "error" ? "!" : "i";
      }
      if (title) title.textContent = dialog.title || "";
      if (subtitle) subtitle.textContent = dialog.kind === "confirm" ? "確認" : dialog.kind === "error" ? "エラー" : "お知らせ";
      if (message) message.innerHTML = escapeHtml(dialog.message || "").replaceAll("\n", "<br>");
      if (cancelButton) cancelButton.style.display = isConfirm ? "" : "none";
      overlay.classList.add("visible");
    }

    function setBusy(title, message) {
      state.busy = { title, message };
      renderBusy();
    }

    function clearBusy() {
      state.busy = null;
      renderBusy();
    }

    function toast(title, message) {
      return showNotice(title, message);
    }

    function showNotice(title, message) {
      return enqueueDialog({
        kind: "notice",
        title,
        message,
      });
    }

    function confirmDialog(title, message) {
      return enqueueDialog({
        kind: "confirm",
        title,
        message,
      });
    }

    function enqueueDialog(dialog) {
      return new Promise((resolve) => {
        dialogQueue.push({ ...dialog, resolve });
        pumpDialogQueue();
      });
    }

    function pumpDialogQueue() {
      if (activeDialog || !dialogQueue.length) {
        return;
      }
      activeDialog = dialogQueue.shift();
      state.dialog = activeDialog;
      renderDialog();
    }

    function closeDialog(result) {
      const dialog = activeDialog;
      activeDialog = null;
      state.dialog = null;
      renderDialog();
      if (dialog && typeof dialog.resolve === "function") {
        dialog.resolve(result);
      }
      pumpDialogQueue();
    }

    function renderCurrentScreen() {
      switch (state.currentScreen) {
        case "lending":
          return renderLendingScreen();
        case "return":
          return renderReturnScreen();
        case "confirmation":
          return renderConfirmationScreen();
        case "pg_master":
          return renderPgMasterScreen();
        case "staff_master":
          return renderStaffMasterScreen();
        default:
          return "";
      }
    }

    function renderLendingScreen() {
      const s = state.lending;
      return `
        <div class="two-col">
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>貸出登録</h3>
                <span class="metric-pill" id="lending-gauge-count">${countEnteredGaugeSizes()}件</span>
              </div>
              <div class="field-group inline">
                <div class="field-label">貸出日</div>
                <input type="date" class="field-control compact" data-screen="lending" data-field="registerDate" value="${escapeHtml(s.registerDate)}" />
              </div>
              <div class="field-group inline">
                <div class="field-label">機番</div>
                <div class="field-row" style="margin:0;">
                  ${renderMachinePicker("lending-register-prefix", s.registerMachinePrefix, lendingMachinePrefixOptions(), false)}
                  <span class="inline-note">-</span>
                  ${renderMachinePicker("lending-register-suffix", s.registerMachineSuffix, state.options.machineSuffixes || [], !s.registerMachinePrefix || s.registerMachinePrefix === state.numberMachinePrefix)}
                  <span class="mini-readout" id="lending-register-machine">${escapeHtml(machineCode(s.registerMachinePrefix, s.registerMachineSuffix))}</span>
                </div>
              </div>
              <div class="field-group inline">
                <div class="field-label">担当者</div>
                <select class="field-control compact" data-screen="lending" data-field="registerStaffId" ${s.registerMachinePrefix ? "" : "disabled"}>
                  ${renderStaffOptions(s.staffMembers, s.registerStaffId, true)}
                </select>
              </div>
              <div class="button-row">
                <button class="btn primary" data-action="lending-register">登録</button>
                <button class="btn secondary" data-action="lending-clear">クリア</button>
              </div>
              <div class="help">20 件分のサイズを入力できます。Enter キーで次の入力欄へ移動します。</div>
              <div style="margin-top:18px;">
                <div class="card-head">
                  <h3>サイズ入力</h3>
                  <span class="inline-note" id="lending-gauge-count-note">入力済み ${countEnteredGaugeSizes()} 件</span>
                </div>
                <div class="size-grid">
                  ${s.registerGaugeSizes.map((value, index) => `
                    <div class="size-row">
                      <div class="size-index">${index + 1}</div>
                      <input class="field-control compact" data-screen="lending" data-field="registerGaugeSizes" data-index="${index}" value="${escapeHtml(value)}" placeholder="サイズ" />
                    </div>
                  `).join("")}
                </div>
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="toolbar">
                <div class="card-head" style="margin:0;">
                  <h3>貸出一覧</h3>
                  <span class="metric-pill">${s.loans.length}件</span>
                </div>
                <div class="field-row" style="margin:0;">
                  <span class="field-label">検索モード</span>
                  <button class="btn filter ${s.searchMode === "size" ? "active" : ""}" data-action="lending-mode" data-mode="size">サイズ</button>
                  <button class="btn filter ${s.searchMode === "machine" ? "active" : ""}" data-action="lending-mode" data-mode="machine">機番</button>
                </div>
              </div>
              <div class="stack">
                <div class="field-row">
                  <div class="field-group search-box" style="flex:1 1 260px;">
                    <div class="field-label">サイズ検索</div>
                    <input class="field-control compact" data-screen="lending" data-field="searchSizePrefix" value="${escapeHtml(s.searchSizePrefix)}" placeholder="サイズ" ${s.searchMode === "size" ? "" : "disabled"} />
                  </div>
                  <label class="field-row" style="margin:0;align-items:center;">
                    <input type="checkbox" data-screen="lending" data-field="useSizePrefixMatch" ${s.useSizePrefixMatch ? "checked" : ""} ${s.searchMode === "size" ? "" : "disabled"} />
                    <span class="field-label">前方一致</span>
                  </label>
                </div>
                <div class="field-row">
                  <div class="field-group" style="margin:0;flex:1;">
                    <div class="field-label">機番</div>
                    <div class="field-row" style="margin:0;">
                      ${renderMachinePicker("lending-search-prefix", s.searchMachinePrefix, lendingMachinePrefixOptions(), s.searchMode !== "machine")}
                      <span class="inline-note">-</span>
                      ${renderMachinePicker("lending-search-suffix", s.searchMachineSuffix, state.options.machineSuffixes || [], s.searchMode !== "machine" || !s.searchMachinePrefix || s.searchMachinePrefix === state.numberMachinePrefix)}
                      <span class="mini-readout" id="lending-search-machine">${escapeHtml(machineCode(s.searchMachinePrefix, s.searchMachineSuffix))}</span>
                    </div>
                  </div>
                </div>
                <div class="button-row">
                  <button class="btn secondary" data-action="lending-search">検索</button>
                  <button class="btn ghost" data-action="lending-list-clear">一覧クリア</button>
                  <button class="btn secondary" data-action="lending-edit" ${s.selectedLoanId ? "" : "disabled"}>選択を編集</button>
                </div>
              </div>
              <div class="table-wrap" style="margin-top:16px;">
                ${renderTable(
                  s.loans,
                  ["貸出日", "機番", "サイズ", "数量", "担当者", "状態"],
                  (row) => [
                    formatDate(row.lent_on),
                    row.machine_code || "",
                    row.size || "",
                    row.holding_count == null ? "" : String(row.holding_count),
                    row.staff_name || "",
                    row.returned_on ? "返却済" : "貸出中"
                  ],
                  s.selectedLoanId,
                  (row) => row.loan_id
                )}
              </div>
            </div>
          </section>
        </div>
      `;
    }

    function renderReturnScreen() {
      const s = state.return;
      return `
        <div class="two-col">
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>返却条件</h3>
                <span class="metric-pill">${s.loans.length}件</span>
              </div>
              <div class="field-group inline">
                <div class="field-label">返却日</div>
                <input type="date" class="field-control compact" data-screen="return" data-field="date" value="${escapeHtml(s.date)}" />
              </div>
              <div class="field-group inline">
                <div class="field-label">機番</div>
                <div class="field-row" style="margin:0;">
                  ${renderMachinePicker("return-prefix", s.machinePrefix, returnMachinePrefixOptions(), false)}
                  <span class="inline-note">-</span>
                  ${renderMachinePicker("return-suffix", s.machineSuffix, state.options.machineSuffixes || [], !s.machinePrefix || s.machinePrefix === state.numberMachinePrefix)}
                  <span class="mini-readout" id="return-machine">${escapeHtml(machineCode(s.machinePrefix, s.machineSuffix))}</span>
                </div>
              </div>
              <div class="field-group inline">
                <div class="field-label">ケースNo</div>
                <input class="field-control compact" maxlength="2" data-screen="return" data-field="caseNo" value="${escapeHtml(s.caseNo)}" placeholder="ケースNo" />
              </div>
              <div class="button-row">
                <button class="btn secondary" data-action="return-search">検索</button>
                <button class="btn ghost" data-action="return-clear">クリア</button>
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>返却対象一覧</h3>
                <span class="metric-pill">${s.loans.length}件</span>
              </div>
              <div class="field-row" style="justify-content:space-between;">
                <div class="inline-note">選択した 1 件だけ返却、または一覧をまとめて返却できます。</div>
                <div class="button-row" style="margin:0;">
                  <button class="btn secondary small" data-action="return-one" ${s.selectedLoanId ? "" : "disabled"}>1件返却</button>
                  <button class="btn primary small" data-action="return-all" ${s.loans.length ? "" : "disabled"}>一括返却</button>
                </div>
              </div>
              <div class="table-wrap">
                ${renderTable(
                  s.loans,
                  ["ID", "サイズ", "担当者", "機番", "貸出日", "ケースNo"],
                  (row) => [row.loan_id, row.size || "", row.staff_name || "", row.machine_code || "", formatDate(row.lent_on), row.case_no || ""],
                  s.selectedLoanId,
                  (row) => row.loan_id
                )}
              </div>
            </div>
          </section>
        </div>
      `;
    }

    function renderConfirmationScreen() {
      const s = state.confirmation;
      return `
        <div class="two-col equal">
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>確認対象</h3>
                <span class="metric-pill">${s.detailLoans.length}件</span>
              </div>
              <div class="field-row">
                <div class="field-group search-box" style="flex:1 1 240px;">
                  <div class="field-label">ケースNo</div>
                  <input class="field-control compact" maxlength="2" data-screen="confirmation" data-field="caseNo" value="${escapeHtml(s.caseNo)}" placeholder="ケースNo" />
                </div>
                <button class="btn secondary" data-action="confirmation-search">検索</button>
              </div>
              <div class="field-row" style="justify-content:space-between;">
                <div class="inline-note">一覧から 1 件を確認、または表示中をまとめて確認できます。</div>
                <div class="button-row" style="margin:0;">
                  <button class="btn secondary small" data-action="confirmation-one" ${s.selectedLoanId ? "" : "disabled"}>1件確認</button>
                  <button class="btn primary small" data-action="confirmation-all" ${s.detailLoans.length ? "" : "disabled"}>一括確認</button>
                </div>
              </div>
              <div class="table-wrap" style="margin-top:12px;">
                ${renderTable(
                  s.detailLoans,
                  ["ID", "サイズ", "担当者", "返却日", "ケースNo", "状態"],
                  (row) => [row.loan_id, row.size || "", row.staff_name || "", formatDate(row.returned_on), row.case_no || "", formatCompletionFlag(row.completion_flag)],
                  s.selectedLoanId,
                  (row) => row.loan_id
                )}
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>確認済みバッチ</h3>
                <button class="btn secondary small" data-action="confirmation-refresh">再読込</button>
              </div>
              <div class="table-wrap">
                ${renderBatchTable(s.batches, s.selectedBatchMachineCode)}
              </div>
            </div>
          </section>
        </div>
      `;
    }

    function renderPgMasterScreen() {
      const s = state.pgMaster;
      return `
        <div class="two-col">
          <section class="card">
            <div class="card-inner">
              <div class="toolbar">
                <div class="card-head" style="margin:0;">
                  <h3>PGマスタ一覧</h3>
                  <span class="metric-pill">${s.rows.length}件</span>
                </div>
                <div class="field-row" style="margin:0;">
                  <div class="field-group search-box" style="margin:0;">
                    <div class="field-label">サイズ検索</div>
                    <input class="field-control compact" data-screen="pg_master" data-field="searchQuery" value="${escapeHtml(s.searchQuery)}" placeholder="サイズ" />
                  </div>
                  <div class="search-actions">
                    <button class="btn secondary" data-action="pg-search">検索</button>
                    <button class="btn neutral" data-action="pg-clear">クリア</button>
                  </div>
                </div>
              </div>
              <div class="table-wrap">
                ${renderTable(
                  s.rows,
                  ["サイズ", "数量", "ケースNo"],
                  (row) => [row.size || "", row.holding_count || "", row.case_no || ""],
                  s.selectedSize,
                  (row) => row.size
                )}
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>編集</h3>
                <span class="metric-pill">${s.isNew ? "新規" : "更新"}</span>
              </div>
              <div class="field-group">
                <div class="field-label">サイズ</div>
                <input class="field-control compact" data-screen="pg_master" data-field="editSize" value="${escapeHtml(s.editSize)}" ${s.isNew ? "" : "disabled"} />
              </div>
              <div class="field-group">
                <div class="field-label">数量</div>
                <input type="number" min="0" class="field-control compact" data-screen="pg_master" data-field="editHoldingCount" value="${escapeHtml(s.editHoldingCount)}" />
              </div>
              <div class="field-group">
                <div class="field-label">ケースNo</div>
                <input class="field-control compact" maxlength="20" data-screen="pg_master" data-field="editCaseNo" value="${escapeHtml(s.editCaseNo)}" />
              </div>
              <div class="button-row">
                <button class="btn secondary" data-action="pg-new">新規</button>
                <button class="btn primary" data-action="pg-save">保存</button>
                <button class="btn ghost" data-action="pg-delete" ${s.selectedSize || s.editSize ? "" : "disabled"}>削除</button>
              </div>
            </div>
          </section>
        </div>
      `;
    }

    function renderStaffMasterScreen() {
      const s = state.staffMaster;
      return `
        <div class="two-col">
          <section class="card">
            <div class="card-inner">
              <div class="toolbar">
                <div class="card-head" style="margin:0;">
                  <h3>担当者一覧</h3>
                  <span class="metric-pill">${s.rows.length}件</span>
                </div>
                <div class="field-row" style="margin:0;">
                  <div class="field-group search-box" style="margin:0;">
                    <div class="field-label">ID / 氏名検索</div>
                    <input class="field-control compact" data-screen="staff_master" data-field="searchQuery" value="${escapeHtml(s.searchQuery)}" placeholder="検索" />
                  </div>
                  <button class="btn secondary" data-action="staff-search">検索</button>
                </div>
              </div>
              <div class="table-wrap">
                ${renderTable(
                  s.rows,
                  ["担当者ID", "氏名", "部署", "かな", "表示"],
                  (row) => [row.staff_id || "", row.name || "", row.department || "", row.kana || "", row.visible ? "Y" : "N"],
                  s.selectedStaffId,
                  (row) => row.staff_id
                )}
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>編集</h3>
                <span class="metric-pill">保存用</span>
              </div>
              <div class="field-group">
                <div class="field-label">担当者ID</div>
                <input class="field-control compact" data-screen="staff_master" data-field="editStaffId" value="${escapeHtml(s.editStaffId)}" disabled />
              </div>
              <div class="field-group">
                <div class="field-label">氏名</div>
                <input class="field-control compact" data-screen="staff_master" data-field="editName" value="${escapeHtml(s.editName)}" />
              </div>
              <div class="field-group">
                <div class="field-label">部署</div>
                <select class="field-control compact" data-screen="staff_master" data-field="editDepartment">
                  ${renderOptions(state.options.departments, s.editDepartment)}
                </select>
              </div>
              <div class="field-group">
                <div class="field-label">かな</div>
                <input class="field-control compact" data-screen="staff_master" data-field="editKana" value="${escapeHtml(s.editKana)}" />
              </div>
              <label class="field-row" style="margin:4px 0 0;align-items:center;">
                <input type="checkbox" data-screen="staff_master" data-field="editVisible" ${s.editVisible ? "checked" : ""} />
                <span class="field-label">表示する</span>
              </label>
              <div class="button-row">
                <button class="btn primary" data-action="staff-save">保存</button>
              </div>
            </div>
          </section>
        </div>
      `;
    }

    function renderOptions(values, selected) {
      return values.map((value) => `<option value="${escapeHtml(value)}" ${String(value) === String(selected) ? "selected" : ""}>${escapeHtml(value)}</option>`).join("");
    }

    function renderStaffOptions(rows, selectedId, includeBlank) {
      const parts = [];
      if (includeBlank) {
        parts.push('<option value="">-- 選択してください --</option>');
      }
      if (!rows.length) {
        parts.push('<option value="">該当なし</option>');
        return parts.join("");
      }
      for (const row of rows) {
        const selected = String(row.staff_id ?? "") === String(selectedId ?? "");
        parts.push(`<option value="${escapeHtml(row.staff_id ?? "")}" ${selected ? "selected" : ""}>${escapeHtml(row.name ?? row.staff_id ?? "")}</option>`);
      }
      return parts.join("");
    }

    function machinePickerBinding(pickerId) {
      switch (pickerId) {
        case "lending-register-prefix":
          return { screen: "lending", field: "registerMachinePrefix", id: "lending-register-machine-prefix", kind: "prefix" };
        case "lending-register-suffix":
          return { screen: "lending", field: "registerMachineSuffix", id: "lending-register-machine-suffix", kind: "suffix" };
        case "lending-search-prefix":
          return { screen: "lending", field: "searchMachinePrefix", id: "lending-search-machine-prefix", kind: "prefix" };
        case "lending-search-suffix":
          return { screen: "lending", field: "searchMachineSuffix", id: "lending-search-machine-suffix", kind: "suffix" };
        case "return-prefix":
          return { screen: "return", field: "machinePrefix", id: "return-machine-prefix", kind: "prefix" };
        case "return-suffix":
          return { screen: "return", field: "machineSuffix", id: "return-machine-suffix", kind: "suffix" };
        case "loan-edit-prefix":
          return { screen: "loanEdit", field: "prefix", id: "loan-edit-machine-prefix", kind: "prefix" };
        case "loan-edit-suffix":
          return { screen: "loanEdit", field: "suffix", id: "loan-edit-machine-suffix", kind: "suffix" };
        default:
          return null;
      }
    }

    function orderMachinePickerOptions(binding, options, current) {
      const unique = [];
      const seen = new Set();
      const currentText = String(current ?? "");
      const source = Array.isArray(options)
        ? options.filter((option) => String(option ?? "") !== "")
        : [];
      if (currentText && !source.some((option) => String(option ?? "") === currentText)) {
        source.unshift(currentText);
      }
      if (binding && binding.kind === "prefix") {
        const preferred = binding.screen === "lending"
          ? ["A", "B", "C", "D", "E", "F", state.numberMachinePrefix, "返"].filter(Boolean)
          : ["A", "B", "C", "D", "E", "F", state.numberMachinePrefix].filter(Boolean);
        for (const option of preferred) {
          const optionText = String(option ?? "");
          if (!optionText || seen.has(optionText)) continue;
          if (source.some((item) => String(item ?? "") === optionText)) {
            seen.add(optionText);
            unique.push(optionText);
          }
        }
      }
      for (const option of source) {
        const optionText = String(option ?? "");
        if (seen.has(optionText)) continue;
        seen.add(optionText);
        unique.push(optionText);
      }
      return unique;
    }

    function renderMachinePicker(pickerId, value, options, disabled, placeholder = "(未入力)", width = "96px") {
      const binding = machinePickerBinding(pickerId);
      if (!binding) return "";
      const current = String(value ?? "");
      const uniqueOptions = orderMachinePickerOptions(binding, options, current);
      return `
        <select
          class="field-control compact"
          id="${escapeHtml(binding.id)}"
          data-screen="${escapeHtml(binding.screen)}"
          data-field="${escapeHtml(binding.field)}"
          style="width:${escapeHtml(width)};"
          ${disabled ? "disabled" : ""}
        >
          <option value="">${escapeHtml(placeholder)}</option>
          ${uniqueOptions.map((option) => {
            const selected = option === current;
            return `<option value="${escapeHtml(option)}" ${selected ? "selected" : ""}>${escapeHtml(option)}</option>`;
          }).join("")}
        </select>
      `;
    }

    function lendingMachinePrefixOptions() {
      return state.options.lendingMachinePrefixes || [];
    }

    function returnMachinePrefixOptions() {
      return state.options.returnMachinePrefixes || [];
    }

    function renderTable(rows, headers, rowMapper, selectedValue, valueExtractor) {
      if (!rows || !rows.length) {
        return '<div class="empty-state">データがありません。</div>';
      }
      const head = headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("");
      const body = rows.map((row, index) => {
        const selected = String(selectedValue ?? "") === String(valueExtractor(row, index) ?? "");
        const values = rowMapper(row, index).map((value) => `<td>${escapeHtml(value)}</td>`).join("");
        return `<tr data-action="select-row" data-row-index="${index}" class="${rowClasses(selected)}">${values}</tr>`;
      }).join("");
      return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    }

    function renderBatchTable(rows, selectedMachineCode) {
      if (!rows || !rows.length) {
        return '<div class="empty-state">確認済みバッチはありません。</div>';
      }
      const head = '<tr><th>機番</th><th>返却日</th></tr>';
      const body = rows.map((row, index) => {
        const selected = String(selectedMachineCode ?? "") === String(row.machine_code ?? "");
        return `<tr data-action="select-batch" data-row-index="${index}" class="${rowClasses(selected)}"><td>${escapeHtml(row.machine_code ?? "")}</td><td>${escapeHtml(formatDate(row.returned_on))}</td></tr>`;
      }).join("");
      return `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
    }

    function countEnteredGaugeSizes() {
      return state.lending.registerGaugeSizes.filter((value) => String(value || "").trim()).length;
    }

    function applyLendingPreview() {
      const register = document.getElementById("lending-register-machine");
      const search = document.getElementById("lending-search-machine");
      const registerPrefix = state.lending.registerMachinePrefix;
      const searchPrefix = state.lending.searchMachinePrefix;
      const isRegisterNumber = registerPrefix === state.numberMachinePrefix;
      const isSearchNumber = searchPrefix === state.numberMachinePrefix;

      if (!registerPrefix || isRegisterNumber) {
        state.lending.registerMachineSuffix = "";
        const suffix = document.querySelector('[data-screen="lending"][data-field="registerMachineSuffix"]');
        if (suffix) suffix.value = "";
      }
      if (!searchPrefix || isSearchNumber) {
        state.lending.searchMachineSuffix = "";
        const suffix = document.querySelector('[data-screen="lending"][data-field="searchMachineSuffix"]');
        if (suffix) suffix.value = "";
      }
      if (register) register.textContent = machineCode(state.lending.registerMachinePrefix, state.lending.registerMachineSuffix);
      if (search) search.textContent = machineCode(state.lending.searchMachinePrefix, state.lending.searchMachineSuffix);

      const staff = document.querySelector('[data-screen="lending"][data-field="registerStaffId"]');
      const registerSuffix = document.querySelector('[data-screen="lending"][data-field="registerMachineSuffix"]');
      const searchSuffix = document.querySelector('[data-screen="lending"][data-field="searchMachineSuffix"]');
      if (staff) staff.disabled = !state.lending.registerMachinePrefix;
      if (registerSuffix) registerSuffix.disabled = !state.lending.registerMachinePrefix || isRegisterNumber;
      if (searchSuffix) searchSuffix.disabled = state.lending.searchMode !== "machine" || !state.lending.searchMachinePrefix || isSearchNumber;
    }

    function applyReturnPreview() {
      const display = document.getElementById("return-machine");
      const suffix = document.querySelector('[data-screen="return"][data-field="machineSuffix"]');
      const isNumber = state.return.machinePrefix === state.numberMachinePrefix;
      if (!state.return.machinePrefix || isNumber) {
        state.return.machineSuffix = "";
        if (suffix) suffix.value = "";
      }
      if (display) display.textContent = machineCode(state.return.machinePrefix, state.return.machineSuffix);
      if (suffix) suffix.disabled = !state.return.machinePrefix || isNumber;
    }

    function updateLoanEditMachinePreview() {
      const display = document.getElementById("loan-edit-machine");
      if (!display) {
        return;
      }
      if (!state.loanEditMachinePrefix || state.loanEditMachinePrefix === state.numberMachinePrefix) {
        state.loanEditMachineSuffix = "";
      }
      display.textContent = machineCode(state.loanEditMachinePrefix, state.loanEditMachineSuffix);
    }

    function updateLendingGaugeCountDisplay() {
      const text = `${countEnteredGaugeSizes()}件`;
      const count = document.getElementById("lending-gauge-count");
      const note = document.getElementById("lending-gauge-count-note");
      if (count) count.textContent = text;
      if (note) note.textContent = `入力済み ${countEnteredGaugeSizes()} 件`;
    }

    async function invokeApi(name, payload) {
      const api = window.pywebview && window.pywebview.api;
      if (!api) throw new Error("pywebview API is not ready.");
      if (typeof api[name] !== "function") {
        throw new Error(`API method not ready: ${name}`);
      }
      const result = payload === undefined ? await api[name]() : await api[name](payload);
      if (!result || result.ok === false) {
        throw new Error(result && result.message ? result.message : "処理に失敗しました。");
      }
      return result.data || {};
    }

    async function bootstrap() {
      const payload = await invokeApi("bootstrap");
      state.appName = payload.app_name || state.appName;
      state.databaseBackend = payload.database_backend || "";
      state.currentDate = payload.current_date || "";
      state.screenTitles = payload.screen_titles || state.screenTitles;
      const options = payload.options || {};
      state.options = {
        lendingMachinePrefixes: options.lending_machine_prefixes || [],
        returnMachinePrefixes: options.return_machine_prefixes || [],
        machineSuffixes: options.machine_suffixes || [],
        departments: options.departments || [],
      };
      state.numberMachinePrefix = payload.number_machine_prefix || "";
      state.initialErrors = payload.initial_errors || [];
      state.lending.registerDate = payload.lending.register_date || state.currentDate;
      state.lending.loans = payload.lending.loans || [];
      state.return.date = payload.return.date || state.currentDate;
      state.return.loans = payload.return.loans || [];
      state.confirmation.batches = payload.confirmation.batches || [];
      state.pgMaster.rows = payload.pg_master.rows || [];
      state.staffMaster.rows = payload.staff_master.rows || [];
      renderApp();
      state.busy = null;
      renderBusy();
      if (state.initialErrors.length) {
        for (const message of state.initialErrors) {
          await toast("起動時エラー", message);
        }
        state.initialErrors = [];
      }
    }

    function setBoundValue(target) {
      const screen = target.dataset.screen;
      const field = target.dataset.field;
      const index = target.dataset.index;
      const value = readValue(target);
      if (screen === "loanEdit") {
        if (field === "prefix") {
          state.loanEditMachinePrefix = value;
          if (!value || value === state.numberMachinePrefix) {
            state.loanEditMachineSuffix = "";
          }
          return;
        }
        if (field === "suffix") {
          state.loanEditMachineSuffix = value;
          return;
        }
      }
      const screenState = state[screen];
      if (!screenState) return;
      if (index !== undefined) {
        screenState[field][Number(index)] = value;
      } else {
        screenState[field] = value;
      }
    }

    function readValue(target) {
      if (target instanceof HTMLInputElement && target.type === "checkbox") return target.checked;
      if (target instanceof HTMLInputElement && target.type === "number") return target.value === "" ? 0 : Number(target.value);
      return target.value;
    }

    function getInputValue(selector, fallback = "") {
      const element = document.querySelector(selector);
      if (element instanceof HTMLInputElement || element instanceof HTMLSelectElement || element instanceof HTMLTextAreaElement) {
        return element.value;
      }
      return fallback;
    }

    function getCheckboxValue(selector, fallback = false) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLInputElement && element.type === "checkbox") {
        return element.checked;
      }
      return fallback;
    }

    function selectRowFromCurrentScreen(index) {
      switch (state.currentScreen) {
        case "lending":
          state.lending.selectedLoanId = state.lending.loans[index] ? state.lending.loans[index].loan_id : null;
          break;
        case "return":
          state.return.selectedLoanId = state.return.loans[index] ? state.return.loans[index].loan_id : null;
          break;
        case "confirmation":
          state.confirmation.selectedLoanId = state.confirmation.detailLoans[index] ? state.confirmation.detailLoans[index].loan_id : null;
          break;
        case "pg_master":
          selectPgRow(index);
          break;
        case "staff_master":
          selectStaffRow(index);
          break;
      }
      renderApp();
    }

    function selectPgRow(index) {
      const row = state.pgMaster.rows[index];
      if (!row) return;
      state.pgMaster.selectedSize = row.size || "";
      state.pgMaster.editSize = row.size || "";
      state.pgMaster.editHoldingCount = Number(row.holding_count ?? 0);
      state.pgMaster.editCaseNo = row.case_no || "";
      state.pgMaster.isNew = false;
    }

    function selectStaffRow(index) {
      const row = state.staffMaster.rows[index];
      if (!row) return;
      state.staffMaster.selectedStaffId = row.staff_id || "";
      state.staffMaster.editStaffId = row.staff_id || "";
      state.staffMaster.editName = row.name || "";
      state.staffMaster.editDepartment = row.department || "製造";
      state.staffMaster.editKana = row.kana || "";
      state.staffMaster.editVisible = !!row.visible;
    }

    async function refreshLendingStaffMembers() {
      const prefix = state.lending.registerMachinePrefix || "";
      if (!prefix) {
        state.lending.staffMembers = [];
        state.lending.registerStaffId = "";
        renderApp();
        return;
      }
      const data = await invokeApi("get_staff_members", { machine_prefix: prefix });
      state.lending.staffMembers = data.staff_members || [];
      if (!state.lending.staffMembers.some((row) => String(row.staff_id) === String(state.lending.registerStaffId))) {
        state.lending.registerStaffId = "";
      }
      renderApp();
    }

    async function refreshLendingSearch() {
      const data = await invokeApi("search_lending", {
        search_mode: state.lending.searchMode,
        size_prefix: state.lending.searchSizePrefix,
        machine_prefix: state.lending.searchMachinePrefix,
        machine_suffix: state.lending.searchMachineSuffix,
        use_size_prefix_match: state.lending.useSizePrefixMatch,
      });
      state.lending.loans = data.loans || [];
      state.lending.selectedLoanId = null;
      renderApp();
    }

    async function refreshReturnSearch() {
      const data = await invokeApi("search_returnable_loans", {
        machine_prefix: state.return.machinePrefix,
        machine_suffix: state.return.machineSuffix,
      });
      state.return.loans = data.loans || [];
      state.return.selectedLoanId = null;
      renderApp();
    }

    async function refreshConfirmationSearch() {
      const data = await invokeApi("search_confirmation_loans", { case_no: state.confirmation.caseNo });
      state.confirmation.detailLoans = data.loans || [];
      state.confirmation.selectedLoanId = null;
      renderApp();
    }

    async function refreshConfirmationBatches() {
      const data = await invokeApi("fetch_confirmation_batches");
      state.confirmation.batches = data.batches || [];
      renderApp();
    }

    async function refreshPgMaster() {
      const queryInput = document.querySelector('[data-screen="pg_master"][data-field="searchQuery"]');
      const query = queryInput instanceof HTMLInputElement ? queryInput.value : state.pgMaster.searchQuery;
      state.pgMaster.searchQuery = query;
      const data = await invokeApi("search_pg_master", { size_query: query });
      state.pgMaster.rows = data.rows || [];
      state.pgMaster.selectedSize = "";
      renderApp();
    }

    async function clearPgMasterSearch() {
      state.pgMaster.searchQuery = "";
      const queryInput = document.querySelector('[data-screen="pg_master"][data-field="searchQuery"]');
      if (queryInput instanceof HTMLInputElement) {
        queryInput.value = "";
      }
      await refreshPgMaster();
    }

    async function refreshStaffMaster() {
      const data = await invokeApi("search_staff_master", { query: state.staffMaster.searchQuery });
      state.staffMaster.rows = data.rows || [];
      state.staffMaster.selectedStaffId = "";
      renderApp();
    }

    function clearLendingRegister() {
      state.lending.registerDate = state.currentDate || state.lending.registerDate;
      state.lending.registerMachinePrefix = "";
      state.lending.registerMachineSuffix = "";
      state.lending.registerStaffId = "";
      state.lending.registerGaugeSizes = Array.from({ length: 20 }, () => "");
      state.lending.staffMembers = [];
      state.lending.selectedLoanId = null;
      renderApp();
    }

    function clearLendingSearch() {
      state.lending.searchSizePrefix = "";
      state.lending.searchMachinePrefix = "";
      state.lending.searchMachineSuffix = "";
      state.lending.useSizePrefixMatch = false;
      state.lending.searchMode = "size";
      state.lending.loans = [];
      state.lending.selectedLoanId = null;
      renderApp();
    }

    function clearReturnForm() {
      state.return.date = state.currentDate || state.return.date;
      state.return.machinePrefix = "";
      state.return.machineSuffix = "";
      state.return.caseNo = "";
      state.return.selectedLoanId = null;
      renderApp();
    }

    function clearConfirmationForm() {
      state.confirmation.caseNo = "";
      state.confirmation.detailLoans = [];
      state.confirmation.selectedLoanId = null;
      state.confirmation.selectedBatchMachineCode = "";
      renderApp();
    }

    function resetPgForm() {
      state.pgMaster.selectedSize = "";
      state.pgMaster.editSize = "";
      state.pgMaster.editHoldingCount = 0;
      state.pgMaster.editCaseNo = "";
      state.pgMaster.isNew = true;
      renderApp();
    }

    async function openLoanEditModal() {
      const loan = state.lending.loans.find((row) => String(row.loan_id) === String(state.lending.selectedLoanId));
      if (!loan) return;

      let staffOptions = renderStaffOptions(state.lending.staffMembers, loan.staff_id, true);
      const loanMachine = splitMachineCode(loan.machine_code || "");
      state.loanEditMachinePrefix = loanMachine.prefix;
      state.loanEditMachineSuffix = loanMachine.suffix;
      if (!loan.staff_id || !state.lending.staffMembers.length) {
        try {
          const prefix = (loan.machine_code || "").includes("-") ? loan.machine_code.split("-", 1)[0] : loan.machine_code || "";
          const data = await invokeApi("get_staff_members", { machine_prefix: prefix });
          staffOptions = renderStaffOptions(data.staff_members || [], loan.staff_id, true);
        } catch (_) {
          // fallback to current list
        }
      }

      state.modal = {
        html: `
          <div class="modal-backdrop" data-action="close-modal">
            <div class="modal" data-modal-stop>
              <div class="card-inner">
                <div class="modal-head">
                  <h3>貸出編集</h3>
                  <button class="modal-close" data-action="close-modal">×</button>
                </div>
                <div class="field-group inline">
                  <div class="field-label">貸出日</div>
                  <input type="date" class="field-control compact" id="loan-edit-date" value="${escapeHtml(loan.lent_on || "")}" />
                </div>
                <div class="field-group inline">
                  <div class="field-label">機番</div>
                  <div class="field-row" style="margin:0;">
                    ${renderMachinePicker("loan-edit-prefix", state.loanEditMachinePrefix, lendingMachinePrefixOptions(), false)}
                    <span class="inline-note">-</span>
                    ${renderMachinePicker("loan-edit-suffix", state.loanEditMachineSuffix, state.options.machineSuffixes || [], !state.loanEditMachinePrefix || state.loanEditMachinePrefix === state.numberMachinePrefix)}
                    <span class="mini-readout" id="loan-edit-machine">${escapeHtml(machineCode(state.loanEditMachinePrefix, state.loanEditMachineSuffix))}</span>
                  </div>
                </div>
                <div class="field-group inline">
                  <div class="field-label">サイズ</div>
                  <input class="field-control compact" id="loan-edit-size" value="${escapeHtml(loan.size || "")}" />
                </div>
                <div class="field-group inline">
                  <div class="field-label">担当者</div>
                  <select class="field-control compact" id="loan-edit-staff">
                    ${staffOptions}
                  </select>
                </div>
                <div class="button-row" style="justify-content:flex-end;">
                  <button class="btn ghost" data-action="loan-delete" data-loan-id="${loan.loan_id}">削除</button>
                  <button class="btn primary" data-action="loan-save" data-loan-id="${loan.loan_id}">保存</button>
                </div>
              </div>
            </div>
          </div>
        `,
      };
      renderModal();
    }

    function closeModal() {
      state.modal = null;
      renderModal();
    }

    function extractCaseNo(machineCode) {
      const normalized = String(machineCode || "").trim();
      if (!normalized.includes("-")) return "";
      return normalized.split("-", 1)[1].trim();
    }

    function formatCompletionFlag(value) {
      const normalized = String(value ?? "").trim().toUpperCase();
      if (normalized === "Y") return "確認済";
      if (normalized === "N" || normalized === "") return "未確認";
      return normalized;
    }

    document.addEventListener("click", async (event) => {
      const dialogAction = event.target.closest("[data-dialog-action]");
      if (dialogAction) {
        const action = dialogAction.dataset.dialogAction;
        if (action === "confirm") {
          closeDialog(true);
        } else if (action === "cancel") {
          closeDialog(false);
        }
        return;
      }
      const dialogBackdrop = event.target.closest("[data-dialog-backdrop]");
      if (dialogBackdrop && event.target === dialogBackdrop) {
        closeDialog(activeDialog && activeDialog.kind === "confirm" ? false : true);
        return;
      }
      const target = event.target.closest("[data-action]");
      if (!target) return;
      const action = target.dataset.action;

      if (action === "navigate") {
        state.currentScreen = target.dataset.screen;
        renderApp();
        return;
      }
      if (action === "toggle-master") {
        state.currentScreen = state.currentScreen === "pg_master" ? "staff_master" : "pg_master";
        renderApp();
        return;
      }
      if (action === "select-row") {
        selectRowFromCurrentScreen(Number(target.dataset.rowIndex));
        return;
      }
      if (action === "select-batch") {
        const row = state.confirmation.batches[Number(target.dataset.rowIndex)];
        if (!row) return;
        state.confirmation.selectedBatchMachineCode = row.machine_code || "";
        const caseNo = extractCaseNo(row.machine_code || "");
        if (caseNo && await confirmDialog("確認対象の表示", `${row.machine_code} の確認対象を表示しますか？`)) {
          state.confirmation.caseNo = caseNo;
          await refreshConfirmationSearch();
        } else {
          renderApp();
        }
        return;
      }
      if (action === "close-modal") {
        closeModal();
        return;
      }
      if (action === "lending-mode") {
        state.lending.searchMode = target.dataset.mode;
        renderApp();
        return;
      }

      try {
        switch (action) {
          case "lending-search":
            if (!(await confirmDialog("貸出一覧検索", "貸出一覧を検索しますか？"))) return;
            setBusy("貸出一覧検索", "貸出データを検索しています...");
            await refreshLendingSearch();
            break;
          case "lending-register":
            if (!(await confirmDialog("貸出登録", "入力内容で貸出登録しますか？"))) return;
            setBusy("貸出登録", "貸出データを登録しています...");
            {
              const registerDate = getInputValue('[data-screen="lending"][data-field="registerDate"]', state.lending.registerDate);
              const registerMachinePrefix = getInputValue('[data-screen="lending"][data-field="registerMachinePrefix"]', state.lending.registerMachinePrefix);
              const registerMachineSuffix = getInputValue('[data-screen="lending"][data-field="registerMachineSuffix"]', state.lending.registerMachineSuffix);
              const registerStaffId = getInputValue('[data-screen="lending"][data-field="registerStaffId"]', state.lending.registerStaffId);
              const registerGaugeSizes = Array.from(
                document.querySelectorAll('[data-screen="lending"][data-field="registerGaugeSizes"]')
              ).map((element) => (element instanceof HTMLInputElement ? element.value : ""));
              state.lending.registerDate = registerDate;
              state.lending.registerMachinePrefix = registerMachinePrefix;
              state.lending.registerMachineSuffix = registerMachineSuffix;
              state.lending.registerStaffId = registerStaffId;
              state.lending.registerGaugeSizes = registerGaugeSizes;
              const data = await invokeApi("register_lending", {
                lent_on: registerDate,
                machine_prefix: registerMachinePrefix,
                machine_suffix: registerMachineSuffix,
                staff_id: registerStaffId,
                gauge_sizes: registerGaugeSizes,
              });
              state.lending.loans = data.loans || [];
              clearLendingRegister();
              toast("完了", "貸出登録が完了しました。");
            }
            break;
          case "lending-clear":
            clearLendingRegister();
            break;
          case "lending-list-clear":
            clearLendingSearch();
            break;
          case "lending-edit":
            await openLoanEditModal();
            break;
          case "return-search":
            if (!(await confirmDialog("返却対象検索", "返却対象を検索しますか？"))) return;
            setBusy("返却検索", "返却対象を検索しています...");
            await refreshReturnSearch();
            break;
          case "return-clear":
            clearReturnForm();
            break;
          case "return-one":
            if (!(await confirmDialog("単票返却", "選択した 1 件を返却しますか？"))) return;
            setBusy("単票返却", "返却処理を実行しています...");
            await invokeApi("return_one_loan", {
              loan_id: state.return.selectedLoanId,
              case_no: state.return.caseNo,
              returned_on: state.return.date,
            });
            await refreshReturnSearch();
            clearReturnForm();
            toast("完了", "返却が完了しました。");
            break;
          case "return-all":
            if (!(await confirmDialog("一括返却", "表示中の返却対象をすべて返却しますか？"))) return;
            setBusy("一括返却", "返却処理を実行しています...");
            {
              const data = await invokeApi("return_all_loans", {
                machine_prefix: state.return.machinePrefix,
                machine_suffix: state.return.machineSuffix,
                case_no: state.return.caseNo,
                returned_on: state.return.date,
                target_count: state.return.loans.length,
              });
              await refreshReturnSearch();
              clearReturnForm();
              toast("完了", `${data.count || 0}件の返却が完了しました。`);
            }
            break;
          case "confirmation-search":
            if (!(await confirmDialog("確認対象検索", "確認対象を検索しますか？"))) return;
            setBusy("確認対象検索", "確認対象を検索しています...");
            await refreshConfirmationSearch();
            break;
          case "confirmation-one":
            if (!(await confirmDialog("確認", "選択した 1 件を確認済みにしますか？"))) return;
            setBusy("確認", "確認処理を実行しています...");
            await invokeApi("confirm_one", { loan_id: state.confirmation.selectedLoanId });
            await refreshConfirmationSearch();
            await refreshConfirmationBatches();
            clearConfirmationForm();
            toast("完了", "確認が完了しました。");
            break;
          case "confirmation-all":
            if (!(await confirmDialog("一括確認", "表示中のデータをまとめて確認済みにしますか？"))) return;
            setBusy("一括確認", "確認処理を実行しています...");
            {
              const data = await invokeApi("confirm_all", { loan_ids: state.confirmation.detailLoans.map((row) => row.loan_id) });
              await refreshConfirmationSearch();
              await refreshConfirmationBatches();
              clearConfirmationForm();
              toast("完了", `${data.count || 0}件の確認が完了しました。`);
            }
            break;
          case "confirmation-refresh":
            setBusy("バッチ再読込", "確認済みバッチを更新しています...");
            await refreshConfirmationBatches();
            break;
          case "pg-search":
            if (!(await confirmDialog("PGマスタ検索", "PGマスタを検索しますか？"))) return;
            setBusy("PGマスタ検索", "PGマスタを検索しています...");
            await refreshPgMaster();
            break;
          case "pg-new":
            resetPgForm();
            break;
          case "pg-clear":
            clearPgMasterSearch().catch((error) => toast("処理失敗", error.message || String(error)));
            break;
          case "pg-save":
            if (!(await confirmDialog("PGマスタ保存", "入力内容でPGマスタを保存しますか？"))) return;
            setBusy("PGマスタ保存", "保存しています...");
            {
              const editSize = getInputValue('[data-screen="pg_master"][data-field="editSize"]', state.pgMaster.editSize);
              const editHoldingCount = getInputValue('[data-screen="pg_master"][data-field="editHoldingCount"]', String(state.pgMaster.editHoldingCount || 0));
              const editCaseNo = getInputValue('[data-screen="pg_master"][data-field="editCaseNo"]', state.pgMaster.editCaseNo);
              state.pgMaster.editSize = editSize;
              state.pgMaster.editHoldingCount = Number(editHoldingCount || 0);
              state.pgMaster.editCaseNo = editCaseNo;
              await invokeApi("save_pg_master", {
                size: editSize,
                holding_count: Number(editHoldingCount || 0),
                case_no: editCaseNo,
                is_new: state.pgMaster.isNew,
              });
            }
            await refreshPgMaster();
            toast("完了", "保存が完了しました。");
            break;
          case "pg-delete":
            if (!(await confirmDialog("PGマスタ削除", "選択中のサイズを削除しますか？"))) return;
            setBusy("PGマスタ削除", "削除しています...");
            {
              const editSize = getInputValue('[data-screen="pg_master"][data-field="editSize"]', state.pgMaster.editSize || state.pgMaster.selectedSize);
              state.pgMaster.editSize = editSize;
              await invokeApi("delete_pg_master", { size: editSize || state.pgMaster.selectedSize });
            }
            resetPgForm();
            await refreshPgMaster();
            toast("完了", "削除が完了しました。");
            break;
          case "staff-search":
            if (!(await confirmDialog("担当者検索", "担当者マスタを検索しますか？"))) return;
            setBusy("担当者検索", "担当者マスタを検索しています...");
            await refreshStaffMaster();
            break;
          case "staff-save":
            if (!(await confirmDialog("担当者保存", "入力内容で担当者情報を保存しますか？"))) return;
            setBusy("担当者保存", "保存しています...");
            {
              const visibleInput = document.querySelector('[data-screen="staff_master"][data-field="editVisible"]');
              const nameInput = document.querySelector('[data-screen="staff_master"][data-field="editName"]');
              const kanaInput = document.querySelector('[data-screen="staff_master"][data-field="editKana"]');
              if (nameInput instanceof HTMLInputElement) state.staffMaster.editName = nameInput.value;
              if (kanaInput instanceof HTMLInputElement) state.staffMaster.editKana = kanaInput.value;
              if (visibleInput instanceof HTMLInputElement) state.staffMaster.editVisible = visibleInput.checked;
            }
            await invokeApi("update_staff_member", {
              staff_id: state.staffMaster.editStaffId,
              name: state.staffMaster.editName,
              department: state.staffMaster.editDepartment,
              kana: state.staffMaster.editKana,
              visible: state.staffMaster.editVisible,
            });
            await refreshStaffMaster();
            toast("完了", "保存が完了しました。");
            break;
          case "loan-save":
            if (!(await confirmDialog("貸出編集", "選択中の貸出を保存しますか？"))) return;
            setBusy("貸出編集", "保存しています...");
            {
              const loanId = Number(target.dataset.loanId);
              const lentOn = document.getElementById("loan-edit-date").value;
              const machinePrefixValue = state.loanEditMachinePrefix;
              const machineSuffixValue = state.loanEditMachineSuffix;
              const machineCodeValue = machineCode(machinePrefixValue, machineSuffixValue);
              const staffId = document.getElementById("loan-edit-staff").value;
              const size = document.getElementById("loan-edit-size").value;
              await invokeApi("update_loan", {
                loan_id: loanId,
                lent_on: lentOn,
                machine_code: machineCodeValue,
                staff_id: staffId,
                size,
              });
              const row = state.lending.loans.find((item) => String(item.loan_id) === String(loanId));
              if (row) {
                row.lent_on = lentOn;
                row.machine_code = machineCodeValue;
                row.staff_id = staffId;
                row.size = size;
                const staff = state.lending.staffMembers.find((item) => String(item.staff_id) === String(staffId));
                if (staff) {
                  row.staff_name = staff.name || row.staff_name;
                }
              }
            }
            closeModal();
            renderApp();
            toast("完了", "保存が完了しました。");
            break;
          case "loan-delete":
            if (!(await confirmDialog("貸出削除", "選択中の貸出を削除しますか？"))) return;
            setBusy("貸出削除", "削除しています...");
            {
              const loanId = Number(target.dataset.loanId);
              await invokeApi("delete_loan", { loan_id: loanId });
              state.lending.loans = state.lending.loans.filter((item) => String(item.loan_id) !== String(loanId));
              state.lending.selectedLoanId = null;
            }
            closeModal();
            renderApp();
            toast("完了", "削除が完了しました。");
            break;
        }
      } catch (error) {
        toast("処理失敗", error.message || String(error));
      } finally {
        clearBusy();
      }
    });

    document.addEventListener("input", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const screen = target.dataset.screen;
      const field = target.dataset.field;
      if (!screen || !field) return;
      setBoundValue(target);
      if (screen === "lending") {
        applyLendingPreview();
        if (field === "registerGaugeSizes") {
          updateLendingGaugeCountDisplay();
        }
      }
      if (screen === "return") {
        applyReturnPreview();
      }
      if (target.id === "loan-edit-machine-prefix" || target.id === "loan-edit-machine-suffix") {
        updateLoanEditMachinePreview();
      }
    });

    document.addEventListener("change", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      const screen = target.dataset.screen;
      const field = target.dataset.field;
      if (!screen || !field) return;
      setBoundValue(target);
      if (screen === "lending" && field === "registerMachinePrefix") {
        refreshLendingStaffMembers().catch((error) => toast("処理失敗", error.message || String(error)));
      }
      if (screen === "lending" && field === "searchMachinePrefix") {
        applyLendingPreview();
      }
      if (screen === "return" && field === "machinePrefix") {
        applyReturnPreview();
      }
      if (target.id === "loan-edit-machine-prefix" || target.id === "loan-edit-machine-suffix") {
        updateLoanEditMachinePreview();
      }
    });

    function startApp() {
      if (state.__started) {
        return;
      }
      if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.bootstrap !== "function") {
        return;
      }
      state.__started = true;
      bootstrap().catch((error) => {
        const app = document.getElementById("app");
        if (app) {
          app.innerHTML = `<div style="padding:24px;color:#a34d58;font-weight:700;">起動失敗: ${escapeHtml(error.message || String(error))}</div>`;
        }
        toast("起動失敗", error.message || String(error));
      });
    }

    window.addEventListener("pywebviewready", startApp);
    document.addEventListener("DOMContentLoaded", () => {
      state.busy = { title: "起動中", message: "アプリを準備しています..." };
      renderBusy();
      startApp();
      const timer = window.setInterval(() => {
        if (state.__started) {
          window.clearInterval(timer);
          return;
        }
        startApp();
      }, 100);
    });

    document.addEventListener("click", (event) => {
      const modal = event.target.closest("[data-modal-stop]");
      if (modal) {
        event.stopPropagation();
      }
    });
  </script>
</body>
</html>
"""
