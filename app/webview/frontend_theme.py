"""配色と、端末内に保存する表示モード。"""

THEME_STYLES = r"""
    :root { color-scheme: light; --color-selected-text: #102235; --color-overlay: rgba(244, 248, 252, 0.86); }
    :root[data-theme="dark"] {
      color-scheme: dark;
      --color-surface: #26313e;
      --color-surface-secondary: #1c2530;
      --color-surface-tertiary: #334254;
      --color-border: #536478;
      --color-border-subtle: #3b4a5c;
      --color-text: #eef3f8;
      --color-text-secondary: #c3cedb;
      --color-text-tertiary: #a7b6c8;
      --color-accent: #2584d4;
      --color-accent-hover: #1766b0;
      --color-accent-soft: rgba(86, 171, 248, 0.20);
      --color-accent-ring: rgba(112, 190, 255, 0.45);
      --color-danger: #ff8e96;
      --color-danger-soft: rgba(255, 142, 150, 0.14);
      --color-selected-text: #ffffff;
      --color-overlay: rgba(20, 28, 38, 0.86);
    }
    tbody tr.selected { color: var(--color-selected-text); }
    .busy-overlay, .dialog-overlay { background: var(--color-overlay); }
    .busy-card, .dialog-card { background: var(--color-surface); }
    [data-theme="dark"] .brand-logo { filter: brightness(0) invert(1); }
    [data-theme="dark"] .metric-pill,
    [data-theme="dark"] .btn.filter.active { color: #9cd4ff; }
    [data-theme="dark"] .btn.danger { background: #bb3545; border-color: #bb3545; }
    [data-theme="dark"] .dialog-mark.confirm { color: #9cd4ff; }
    [data-theme="dark"] .return-search-button:focus { color: #9cd4ff; }
    .field-control::placeholder { color: var(--color-text-tertiary); opacity: 1; }
    .theme-toggle { margin-top: auto; white-space: nowrap; }
    .sidebar-footer { margin-top: 0; }
    .sidebar.collapsed .theme-toggle { min-width: 0; padding: 0; font-size: 18px; }
"""

THEME_SCRIPT = r"""
    let displayTheme = "__INITIAL_THEME__";
    function applyTheme() {
      document.documentElement.dataset.theme = displayTheme;
      const button = document.querySelector('[data-action="toggle-theme"]');
      if (button) {
        const dark = displayTheme === "dark";
        const label = dark ? "ライトモードに切替" : "ダークモードに切替";
        button.textContent = document.querySelector(".sidebar.collapsed") ? (dark ? "☀" : "☾") : label;
        button.setAttribute("aria-label", label);
        button.setAttribute("title", label);
        button.setAttribute("aria-pressed", String(dark));
      }
    }
    async function setTheme(theme) {
      displayTheme = theme === "dark" ? "dark" : "light";
      applyTheme();
      const button = document.querySelector('[data-action="toggle-theme"]');
      if (button) button.disabled = true;
      try {
        await invokeApi("save_theme", { theme: displayTheme });
      } catch (error) {
        console.error("表示モードを保存できませんでした。", error);
        toast("表示設定", "表示モードを保存できませんでした。次回起動時に引き継がれない場合があります。");
      } finally {
        if (button) button.disabled = false;
      }
    }
    applyTheme();
"""
