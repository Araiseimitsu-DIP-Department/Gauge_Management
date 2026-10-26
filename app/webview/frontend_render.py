SCRIPT = r"""
    const state = {
      appName: "__APP_NAME__",
      currentDate: "",
      startupDate: "",
      screenTitles: {
        lending: { title: "貸出", subtitle: "貸出登録と貸出一覧" },
        return: { title: "返却", subtitle: "返却対象の検索と返却処理" },
        confirmation: { title: "確認", subtitle: "返却済みデータの確認処理" },
        pg_master: { title: "PGマスタ", subtitle: "PGマスタの検索と編集" },
        staff_master: { title: "担当者マスタ", subtitle: "担当者情報の編集" },
      },
      currentScreen: "lending",
      initialErrors: [],
      gaugeAutoAdvanceTimer: null,
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
        registerGaugeSizes: Array.from({ length: 30 }, () => ""),
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
        selectedBatchReturnedOn: "",
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
      sidebarCollapsed: false,
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

    function icon(name) {
      const icons = {
        menu: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
        lending: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 4v16M5 11l7-7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        return: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 20V4M19 13l-7 7-7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        confirmation: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m9 12 2 2 4-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M21 12a9 9 0 1 1-3.2-6.9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        master: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 3 4 7v10l8 4 8-4V7l-8-4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="m4 7 8 4 8-4M12 11v10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        pg_master: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.8"/><path d="M9 9h6M9 12h6M9 15h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
        staff_master: '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="9.5" cy="7" r="3" stroke="currentColor" stroke-width="1.8"/><path d="M17 11a3 3 0 1 0 0-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
      };
      return icons[name] || icons.menu;
    }

    function renderNavButton({ screen = "", label, iconName, active, action = "navigate", title = "", extraClass = "" }) {
      const attrs = action === "navigate" ? `data-screen="${escapeHtml(screen)}"` : "";
      return `
        <button
          class="${escapeHtml(extraClass)} ${active ? "active" : ""}"
          data-action="${escapeHtml(action)}"
          ${attrs}
          title="${escapeHtml(title || label)}"
        >
          <span class="nav-icon">${icon(iconName)}</span>
          <span class="nav-label">${escapeHtml(label)}</span>
        </button>
      `;
    }

    function renderApp() {
      const screenClass = `screen ${state.currentScreen}-screen`;
      const app = document.getElementById("app");
      document.documentElement.style.setProperty("--sidebar-width", state.sidebarCollapsed ? "4rem" : "11rem");
      document.body.classList.toggle("lending-active", state.currentScreen === "lending");
      document.body.classList.toggle("return-active", state.currentScreen === "return");
      if (!state.shellRendered || !app.firstElementChild) {
        app.innerHTML = `
          <div class="shell">
            <aside class="sidebar ${state.sidebarCollapsed ? "collapsed" : ""}">
              <div class="brand">
                <div class="brand-main">
                  <img class="brand-logo" src="__ARAI_LOGO__" alt="新井精密" />
                  <div class="brand-mark" aria-hidden="true">A</div>
                  <div class="brand-caption">${escapeHtml(state.appName)}</div>
                </div>
                <button
                  class="sidebar-toggle"
                  data-action="toggle-sidebar"
                  aria-label="${state.sidebarCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}"
                  title="${state.sidebarCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ"}"
                >
                  <span class="nav-icon">${icon("menu")}</span>
                </button>
              </div>
              <div class="nav-group">
                ${renderNavButton({ screen: "lending", label: "貸出", iconName: "lending", active: state.currentScreen === "lending", extraClass: "nav-btn" })}
                ${renderNavButton({ screen: "return", label: "返却", iconName: "return", active: state.currentScreen === "return", extraClass: "nav-btn" })}
                ${renderNavButton({ screen: "confirmation", label: "確認", iconName: "confirmation", active: state.currentScreen === "confirmation", extraClass: "nav-btn" })}
              </div>
              ${renderNavButton({
                label: "マスタ管理",
                iconName: "master",
                active: state.currentScreen === "pg_master" || state.currentScreen === "staff_master",
                action: "toggle-master",
                extraClass: "nav-group-btn",
              })}
              <div class="nav-sub-list" style="display:${!state.sidebarCollapsed && (state.currentScreen === "pg_master" || state.currentScreen === "staff_master") ? "grid" : "none"}">
                ${renderNavButton({ screen: "pg_master", label: "PGマスタ", iconName: "pg_master", active: state.currentScreen === "pg_master", extraClass: "nav-sub-btn" })}
                ${renderNavButton({ screen: "staff_master", label: "担当者マスタ", iconName: "staff_master", active: state.currentScreen === "staff_master", extraClass: "nav-sub-btn" })}
              </div>
              <button class="btn secondary theme-toggle" data-action="toggle-theme" aria-pressed="false">ダークモード</button>
              <div class="sidebar-footer">
                <div>DB: ${escapeHtml(state.databaseBackend || "")}</div>
                <div>起動日: ${escapeHtml(state.startupDate || "")}</div>
              </div>
            </aside>
            <main class="main">
              <div class="main-shell">
                <div class="${screenClass}" id="screen-root">${renderCurrentScreen()}</div>
                <footer class="app-footer"><span class="app-version">v__APP_VERSION__</span> · © ARAISEIMITSU 2026 - Created By DIP Department</footer>
              </div>
            </main>
          </div>
        `;
        state.shellRendered = true;
      } else {
        const screenRoot = document.getElementById("screen-root");
        const sidebar = document.querySelector(".sidebar");
        const navButtons = Array.from(document.querySelectorAll("[data-action=\"navigate\"]"));
        const masterButton = document.querySelector("[data-action=\"toggle-master\"]");
        const sidebarToggle = document.querySelector("[data-action=\"toggle-sidebar\"]");
        const subList = document.querySelector(".nav-sub-list");
        if (screenRoot) {
          screenRoot.className = screenClass;
          screenRoot.innerHTML = renderCurrentScreen();
        }
        if (sidebar) sidebar.classList.toggle("collapsed", state.sidebarCollapsed);
        for (const button of navButtons) {
          const screen = button.dataset.screen;
          button.classList.toggle("active", screen === state.currentScreen);
        }
        if (masterButton) {
          masterButton.classList.toggle("active", state.currentScreen === "pg_master" || state.currentScreen === "staff_master");
        }
        if (sidebarToggle) {
          const label = state.sidebarCollapsed ? "サイドバーを展開" : "サイドバーを折りたたむ";
          sidebarToggle.setAttribute("aria-label", label);
          sidebarToggle.setAttribute("title", label);
        }
        if (subList) {
          subList.style.display = !state.sidebarCollapsed && (state.currentScreen === "pg_master" || state.currentScreen === "staff_master") ? "grid" : "none";
        }
      }
      applyTheme();
      renderModal();
      renderBusy();
      observeConfirmationTable();
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
        <div class="two-col lending-layout">
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
              <div class="help">30 件分のサイズを入力できます。Enter キーで次の入力欄へ移動します。</div>
              <div class="lending-size-section">
                <div class="card-head">
                  <h3>サイズ入力</h3>
                  <span class="inline-note" id="lending-gauge-count-note">入力済み ${countEnteredGaugeSizes()} 件</span>
                </div>
                <div class="size-grid">
                  ${s.registerGaugeSizes.map((value, index) => `
                    <div class="size-row">
                      <div class="size-index">${index + 1}</div>
                      <input class="field-control compact" inputmode="decimal" autocomplete="off" data-screen="lending" data-field="registerGaugeSizes" data-index="${index}" value="${escapeHtml(value)}" placeholder="サイズ" />
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
      const selectedLoan = selectedReturnLoan();
      const selectedSize = selectedLoan ? selectedLoan.size || "" : "";
      const returnCaseNote = getReturnCaseNoError();
      const hasReturnCaseNo = !returnCaseNote;
      return `
        <div class="return-layout">
          <section class="card">
            <div class="card-inner">
              <div class="return-search-row">
                <div class="field-group" style="margin:0;">
                  <div class="field-label">機番</div>
                  <div class="field-row" style="margin:0;">
                    ${renderMachinePicker("return-prefix", s.machinePrefix, returnMachinePrefixOptions(), false)}
                    <span class="inline-note">-</span>
                    ${renderMachinePicker("return-suffix", s.machineSuffix, state.options.machineSuffixes || [], !s.machinePrefix || s.machinePrefix === state.numberMachinePrefix)}
                    <span class="mini-readout" id="return-machine">${escapeHtml(machineCode(s.machinePrefix, s.machineSuffix))}</span>
                  </div>
                </div>
                <div class="return-actions">
                  <button class="btn secondary return-search-button" data-action="return-search">検索</button>
                  <button class="btn ghost" data-action="return-clear">クリア</button>
                </div>
              </div>
            </div>
          </section>
          <section class="card">
            <div class="card-inner">
              <div class="card-head">
                <h3>返却対象一覧</h3>
                <span class="metric-pill">${s.loans.length}件</span>
              </div>
              <div class="return-list-toolbar">
                <div class="field-group" style="margin:0;">
                  <div class="field-label">返却日</div>
                  <input type="date" class="field-control compact" data-screen="return" data-field="date" value="${escapeHtml(s.date)}" />
                </div>
                <div class="field-group return-case-field" style="margin:0;">
                  <div class="return-case-label-row">
                    <div class="field-label">返却ケースNo</div>
                    <div class="return-case-note">${escapeHtml(returnCaseNote)}</div>
                  </div>
                  <input class="field-control compact" maxlength="2" inputmode="numeric" pattern="[0-9]{1,2}" aria-invalid="${!hasReturnCaseNo}" data-screen="return" data-field="caseNo" value="${escapeHtml(s.caseNo)}" placeholder="半角数字1～2桁　例：1、2、3" />
                </div>
                <div aria-hidden="true"></div>
                <div class="return-selected-size">
                  <div class="field-label">選択中のサイズ</div>
                  <div class="value">${escapeHtml(selectedSize || "未選択")}</div>
                </div>
                <div class="return-actions">
                  <button class="btn return-one-action small ${s.selectedLoanId ? "ready" : ""}" data-action="return-one" ${s.selectedLoanId && hasReturnCaseNo ? "" : "disabled"}>個別返却</button>
                  <button class="btn return-all-action small" data-action="return-all" ${s.loans.length && hasReturnCaseNo ? "" : "disabled"}>一括返却</button>
                </div>
              </div>
              <div class="table-wrap">
                ${renderOperationTable(
                  s.loans,
                  ["サイズ", "担当者", "機番", "貸出日", "ケースNo"],
                  (row) => [row.size || "", row.staff_name || "", row.machine_code || "", formatDate(row.lent_on), row.case_no || ""],
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
      const selectedLoan = selectedConfirmationLoan();
      const selectedSize = selectedLoan ? selectedLoan.size || "" : "";
      return `
        <div class="two-col equal">
          <section class="card">
            <div class="card-inner confirmation-workspace">
              <div class="card-head">
                <h3>確認対象</h3>
                <span class="metric-pill">${s.detailLoans.length}件</span>
              </div>
              <div class="confirmation-toolbar">
                <div class="confirmation-search-row">
                  <div class="field-group" style="margin:0;">
                    <div class="field-label">返却ケースNo</div>
                    <input class="field-control compact" maxlength="20" data-screen="confirmation" data-field="caseNo" value="${escapeHtml(s.caseNo)}" placeholder="返却ケースNo" />
                  </div>
                  <button class="btn secondary" data-action="confirmation-search">検索</button>
                </div>
                <div class="confirmation-action-row">
                  <div class="return-selected-size">
                    <div class="field-label">選択中のサイズ</div>
                    <div class="value">${escapeHtml(selectedSize || "未選択")}</div>
                  </div>
                  <div class="return-actions">
                    <button class="btn return-one-action small ${s.selectedLoanId ? "ready" : ""}" data-action="confirmation-one" ${s.selectedLoanId ? "" : "disabled"}>個別確認</button>
                    <button class="btn return-all-action small" data-action="confirmation-all" ${s.detailLoans.length ? "" : "disabled"}>一括確認</button>
                  </div>
                </div>
              </div>
              <div class="table-wrap confirmation-targets" style="margin-top:12px;">
                ${renderTable(
                  s.detailLoans,
                  ["サイズ", "ケースNo", "担当者", "返却日", "状態"],
                  (row) => [row.size || "", row.case_no || "", row.staff_name || "", formatDate(row.returned_on), formatCompletionFlag(row.completion_flag)],
                  s.selectedLoanId,
                  (row) => row.loan_id
                )}
              </div>
            </div>
          </section>
          <section class="card confirmation-batches">
            <div class="card-inner">
              <div class="card-head">
                <h3>確認済みバッチ</h3>
                <div class="button-row" style="margin:0;">
                  <button class="btn secondary small" data-action="confirmation-refresh">再読込</button>
                </div>
              </div>
              <div class="table-wrap">
                ${renderBatchTable(s.batches, s.selectedBatchMachineCode, s.selectedBatchReturnedOn)}
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
              <div class="table-wrap" data-scroll-key="pg-master-list">
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
                <button class="btn danger" data-action="pg-delete" ${s.selectedSize || s.editSize ? "" : "disabled"}>削除</button>
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

"""
