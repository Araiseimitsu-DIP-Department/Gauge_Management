SCRIPT = r"""
    window.addEventListener('resize', syncSidebarLayout);
    document.addEventListener("click", async (event) => {
      syncCurrentDate();
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
        const nextScreen = target.dataset.screen;
        state.currentScreen = nextScreen;
        renderApp();
        if (nextScreen === "confirmation") {
          await refreshConfirmationBatches();
        }
        return;
      }
      if (action === "toggle-theme") {
        await setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
        return;
      }
      if (action === "toggle-sidebar") {
        state.sidebarCollapsed = !state.sidebarCollapsed;
        state.shellRendered = false;
        renderApp();
        return;
      }
      if (action === "toggle-master") {
        if (state.sidebarCollapsed) {
          state.sidebarCollapsed = false;
          state.shellRendered = false;
          renderApp();
          return;
        }
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
        state.confirmation.selectedBatchReturnedOn = row.returned_on || "";
        const caseNo = displayConfirmationCaseNo(row.machine_code || "");
        if (caseNo) {
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
            setBusy("返却検索", "返却対象を検索しています...");
            await refreshReturnSearch();
            break;
          case "return-clear":
            clearReturnForm();
            break;
          case "return-one":
            if (!hasReturnCaseNo()) {
              await showNotice("返却ケースNoを確認してください", getReturnCaseNoError());
              return;
            }
            if (!(await confirmDialog("単票返却", "選択した 1 件を返却しますか？"))) return;
            setBusy("単票返却", "返却処理を実行しています...");
            await invokeApi("return_one_loan", {
              loan_id: state.return.selectedLoanId,
              case_no: state.return.caseNo,
              returned_on: state.return.date,
            });
            await refreshReturnSearch();
            await refreshConfirmationBatches();
            clearReturnSelectionAfterOne();
            toast("完了", "返却が完了しました。");
            break;
          case "return-all":
            if (!hasReturnCaseNo()) {
              await showNotice("返却ケースNoを確認してください", getReturnCaseNoError());
              return;
            }
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
              await refreshConfirmationBatches();
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
            if (!(await confirmDialog("個別確認", "選択した 1 件を確認済みにしますか？"))) return;
            setBusy("個別確認", "確認処理を実行しています...");
            await invokeApi("confirm_one", { loan_id: state.confirmation.selectedLoanId });
            await refreshConfirmationSearch();
            await refreshConfirmationBatches();
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
          if (isLendingGaugeSizeInput(target)) {
            scheduleLendingGaugeAutoAdvance(target);
          }
        }
      }
      if (screen === "return") {
        applyReturnPreview();
        if (field === "caseNo") {
          updateReturnCaseNoControls();
        }
      }
      if (target.id === "loan-edit-machine-prefix" || target.id === "loan-edit-machine-suffix") {
        updateLoanEditMachinePreview();
      }
    });

    document.addEventListener("keydown", (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) return;
      if (event.key !== "Enter") return;
      if (target.dataset.screen !== "return" || target.dataset.field !== "caseNo") return;

      event.preventDefault();
      setBoundValue(target);
      updateReturnCaseNoControls();

      const nextAction = state.return.selectedLoanId
        ? document.querySelector('[data-action="return-one"]')
        : document.querySelector('[data-action="return-all"]');
      if (nextAction && !nextAction.disabled) {
        nextAction.focus();
      } else {
        target.blur();
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
        refreshLendingStaffMembers(true).catch((error) => toast("処理失敗", error.message || String(error)));
      }
      if (screen === "lending" && field === "registerMachineSuffix") {
        focusLendingRegisterNext(field);
      }
      if (screen === "lending" && field === "registerStaffId") {
        focusLendingRegisterNext(field);
      }
      if (screen === "lending" && field === "searchMachinePrefix") {
        applyLendingPreview();
      }
      if (screen === "return" && field === "machinePrefix") {
        applyReturnPreview();
        focusReturnMachineNext(field);
      }
      if (screen === "return" && field === "machineSuffix") {
        applyReturnPreview();
        focusReturnMachineNext(field);
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

    document.addEventListener("keydown", (event) => {
      const target = event.target;
      if (!isLendingGaugeSizeInput(target)) return;
      if (event.key !== "Enter") return;
      event.preventDefault();
      if (state.gaugeAutoAdvanceTimer) {
        window.clearTimeout(state.gaugeAutoAdvanceTimer);
        state.gaugeAutoAdvanceTimer = null;
      }
      focusNextLendingGaugeSizeInput(target);
    });
"""
