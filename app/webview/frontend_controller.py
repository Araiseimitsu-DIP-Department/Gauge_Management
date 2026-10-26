SCRIPT = r"""
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

    function renderTable(rows, headers, rowMapper, selectedValue, valueExtractor, indexOffset = 0) {
      if (!rows || !rows.length) {
        return '<div class="empty-state">データがありません。</div>';
      }
      const head = headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("");
      const body = rows.map((row, localIndex) => {
        const index = localIndex + indexOffset;
        const selected = String(selectedValue ?? "") === String(valueExtractor(row, index) ?? "");
        const values = rowMapper(row, index).map((value) => `<td>${escapeHtml(value)}</td>`).join("");
        return `<tr data-action="select-row" data-row-index="${index}" class="${rowClasses(selected)}">${values}</tr>`;
      }).join("");
      return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    }

    function renderBatchTable(rows, selectedMachineCode, selectedReturnedOn) {
      if (!rows || !rows.length) {
        return '<div class="empty-state">確認済みバッチはありません。</div>';
      }
      const head = '<tr><th>返却ケースNo</th><th>返却日</th></tr>';
      const body = rows.map((row, index) => {
        const selected = String(selectedMachineCode ?? "") === String(row.machine_code ?? "")
          && String(selectedReturnedOn ?? "") === String(row.returned_on ?? "");
        return `<tr data-action="select-batch" data-row-index="${index}" class="${rowClasses(selected)}"><td>${escapeHtml(displayConfirmationCaseNo(row.machine_code))}</td><td>${escapeHtml(formatDate(row.returned_on))}</td></tr>`;
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

    function focusReturnMachineNext(field) {
      window.setTimeout(() => {
        if (field === "machinePrefix") {
          const isNumber = state.return.machinePrefix === state.numberMachinePrefix;
          const next = isNumber
            ? document.querySelector('[data-action="return-search"]')
            : document.getElementById("return-machine-suffix");
          if (next && !next.disabled) next.focus();
          return;
        }
        if (field === "machineSuffix") {
          const searchButton = document.querySelector('[data-action="return-search"]');
          if (searchButton) searchButton.focus();
        }
      }, 0);
    }

    function focusLendingRegisterNext(field) {
      window.setTimeout(() => {
        if (field === "registerMachinePrefix") {
          const isNumber = state.lending.registerMachinePrefix === state.numberMachinePrefix;
          const next = isNumber
            ? document.querySelector('[data-screen="lending"][data-field="registerStaffId"]')
            : document.getElementById("lending-register-machine-suffix");
          if (next && !next.disabled) next.focus();
          return;
        }
        if (field === "registerMachineSuffix") {
          const staff = document.querySelector('[data-screen="lending"][data-field="registerStaffId"]');
          if (staff && !staff.disabled) staff.focus();
          return;
        }
        if (field === "registerStaffId") {
          const firstSize = document.querySelector('[data-screen="lending"][data-field="registerGaugeSizes"][data-index="0"]');
          if (firstSize) {
            firstSize.focus();
            firstSize.select();
          }
        }
      }, 0);
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

    function isLendingGaugeSizeInput(target) {
      return target instanceof HTMLInputElement
        && target.dataset.screen === "lending"
        && target.dataset.field === "registerGaugeSizes";
    }

    function focusNextLendingGaugeSizeInput(current) {
      if (!isLendingGaugeSizeInput(current)) return;
      const currentIndex = Number(current.dataset.index);
      const inputs = Array.from(
        document.querySelectorAll('[data-screen="lending"][data-field="registerGaugeSizes"]')
      ).filter((element) => element instanceof HTMLInputElement);
      const next = inputs.find((element) => Number(element.dataset.index) > currentIndex);
      if (next) {
        next.focus();
        next.select();
      } else {
        current.select();
      }
    }

    function shouldAutoAdvanceLendingGaugeSize(value) {
      const normalized = String(value || "").trim();
      return /^\d+\.\d{3,}$/.test(normalized) || /^\d{4,}$/.test(normalized);
    }

    function scheduleLendingGaugeAutoAdvance(input) {
      if (!isLendingGaugeSizeInput(input)) return;
      if (state.gaugeAutoAdvanceTimer) {
        window.clearTimeout(state.gaugeAutoAdvanceTimer);
      }
      const value = input.value.trim();
      if (!shouldAutoAdvanceLendingGaugeSize(value)) return;
      const index = input.dataset.index;
      state.gaugeAutoAdvanceTimer = window.setTimeout(() => {
        if (document.activeElement === input && input.dataset.index === index && shouldAutoAdvanceLendingGaugeSize(input.value)) {
          focusNextLendingGaugeSizeInput(input);
        }
        state.gaugeAutoAdvanceTimer = null;
      }, 120);
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
      state.startupDate = state.currentDate;
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
      syncCurrentDate();
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

    function getScrollTopByKey(key) {
      const element = document.querySelector(`[data-scroll-key="${key}"]`);
      return element ? element.scrollTop : 0;
    }

    function restoreScrollTopByKey(key, value) {
      const element = document.querySelector(`[data-scroll-key="${key}"]`);
      if (element) {
        element.scrollTop = value;
      }
    }

    function selectRowFromCurrentScreen(index) {
      const pgMasterScrollTop = state.currentScreen === "pg_master" ? getScrollTopByKey("pg-master-list") : null;
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
      if (pgMasterScrollTop !== null) {
        restoreScrollTopByKey("pg-master-list", pgMasterScrollTop);
      }
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

    function selectedReturnLoan() {
      return state.return.loans.find((row) => String(row.loan_id) === String(state.return.selectedLoanId)) || null;
    }

    function hasReturnCaseNo() {
      return getReturnCaseNoError() === "";
    }

    function getReturnCaseNoError() {
      const value = String(state.return.caseNo || "").trim();
      if (!value) return "返却するには返却ケースNoを入力してください。";
      return /^[0-9]{1,2}$/.test(value) ? "" : "返却ケースNoは半角数字1～2桁で入力してください。";
    }

    function selectedConfirmationLoan() {
      return state.confirmation.detailLoans.find((row) => String(row.loan_id) === String(state.confirmation.selectedLoanId)) || null;
    }

    function updateReturnCaseNoControls() {
      const hasCaseNo = hasReturnCaseNo();
      const note = document.querySelector(".return-case-note");
      const oneButton = document.querySelector('[data-action="return-one"]');
      const allButton = document.querySelector('[data-action="return-all"]');

      if (note) {
        note.textContent = getReturnCaseNoError();
      }
      const input = document.querySelector('[data-screen="return"][data-field="caseNo"]');
      if (input) input.setAttribute("aria-invalid", String(!hasCaseNo));
      if (oneButton) {
        oneButton.disabled = !state.return.selectedLoanId || !hasCaseNo;
        oneButton.classList.toggle("ready", !!state.return.selectedLoanId);
      }
      if (allButton) {
        allButton.disabled = !state.return.loans.length || !hasCaseNo;
      }
    }

    async function refreshLendingStaffMembers(focusNext = false) {
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
      if (focusNext) {
        focusLendingRegisterNext("registerMachinePrefix");
      }
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
      state.lending.registerGaugeSizes = Array.from({ length: 30 }, () => "");
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

    function clearReturnSelectionAfterOne() {
      state.return.date = state.currentDate || state.return.date;
      state.return.machinePrefix = "";
      state.return.machineSuffix = "";
      state.return.selectedLoanId = null;
      renderApp();
    }

    function clearConfirmationForm() {
      state.confirmation.caseNo = "";
      state.confirmation.detailLoans = [];
      state.confirmation.selectedLoanId = null;
      state.confirmation.selectedBatchMachineCode = "";
      state.confirmation.selectedBatchReturnedOn = "";
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
                  <button class="btn danger" data-action="loan-delete" data-loan-id="${loan.loan_id}">削除</button>
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

    function displayConfirmationCaseNo(machineCode) {
      const normalized = String(machineCode || "").trim();
      const returnPrefix = "返-";
      if (normalized.startsWith(returnPrefix)) {
        return normalized.slice(returnPrefix.length).trim();
      }
      return normalized;
    }

    function formatCompletionFlag(value) {
      const normalized = String(value ?? "").trim().toUpperCase();
      if (normalized === "Y") return "確認済";
      if (normalized === "N" || normalized === "") return "未確認";
      return normalized;
    }

"""
