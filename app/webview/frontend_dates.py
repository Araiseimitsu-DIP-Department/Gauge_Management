"""開きっぱなしの画面で、PCの現地日付に入力日を追従させる。"""

SCRIPT = r"""
    const DATE_CHECK_INTERVAL_MS = 30 * 1000;

    function syncCurrentDate() {
      if (!state.currentDate) return;
      const now = new Date();
      const today = [now.getFullYear(), String(now.getMonth() + 1).padStart(2, "0"), String(now.getDate()).padStart(2, "0")].join("-");
      if (today === state.currentDate) return;
      state.currentDate = today;
      state.lending.registerDate = today;
      state.return.date = today;
      for (const selector of [
        '[data-screen="lending"][data-field="registerDate"]',
        '[data-screen="return"][data-field="date"]',
      ]) {
        const input = document.querySelector(selector);
        if (input) input.value = today;
      }
    }

    window.setInterval(syncCurrentDate, DATE_CHECK_INTERVAL_MS);
    window.addEventListener("focus", syncCurrentDate);
    window.addEventListener("pageshow", syncCurrentDate);
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) syncCurrentDate();
    });
"""
