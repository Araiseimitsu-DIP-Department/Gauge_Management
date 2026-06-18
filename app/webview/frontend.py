from __future__ import annotations

import base64
import sys
from pathlib import Path


def build_html(app_name: str) -> str:
    return (
        _HTML.replace("__APP_NAME__", _escape_html(app_name))
        .replace("__ARAI_LOGO__", _load_arai_logo_data_uri())
    )


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _load_arai_logo_data_uri() -> str:
    for logo_path in _iter_logo_candidates():
        try:
            encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        except OSError:
            continue
        return f"data:image/png;base64,{encoded}"
    return ""


def _iter_logo_candidates() -> list[Path]:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base = Path(meipass)
            candidates.extend(
                [
                    base / "DESIGN" / "arai_logo.png",
                    base / "arai_logo.png",
                ]
            )
        candidates.append(Path(sys.executable).resolve().parent / "DESIGN" / "arai_logo.png")
    project_root = Path(__file__).resolve().parents[2]
    candidates.extend(
        [
            project_root / "DESIGN" / "arai_logo.png",
            Path.cwd() / "DESIGN" / "arai_logo.png",
        ]
    )

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


_HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__APP_NAME__</title>
  <style>
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
    .header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1.25rem;
    }
    .header h2 {
      margin: 0;
      font-size: 1.5rem;
      line-height: 1.2;
      font-weight: 600;
      letter-spacing: -0.025em;
      color: var(--color-text);
    }
    .header p {
      margin: 0.375rem 0 0;
      color: var(--color-text-secondary);
      font-size: 0.875rem;
      font-weight: 400;
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
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
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
    @media (max-width: 1200px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { border-right: 0; border-bottom: 1px solid rgba(214, 223, 233, 0.8); }
      .two-col, .two-col.equal { grid-template-columns: 1fr; }
      body.lending-active .shell { grid-template-columns: var(--sidebar-width) minmax(0, 1fr); }
      body.lending-active .sidebar {
        border-right: 1px solid var(--color-border);
        border-bottom: 0;
      }
      body.lending-active .main { padding: 0.75rem; }
      body.lending-active .main-shell { min-height: calc(100vh - 1.5rem); }
      body.lending-active .header,
      body.lending-active .app-footer {
        display: none;
      }
      body.lending-active .lending-layout {
        grid-template-columns: minmax(0, 1.25fr) minmax(260px, 0.75fr);
        gap: 0.75rem;
      }
      body.lending-active .lending-layout .size-grid {
        grid-template-columns: repeat(auto-fit, minmax(88px, 1fr));
      }
    }
    @media (max-width: 760px) {
      body.lending-active .shell { grid-template-columns: 1fr; }
      body.lending-active .sidebar {
        border-right: 0;
        border-bottom: 1px solid rgba(214, 223, 233, 0.8);
      }
      body.lending-active .header { display: flex; }
      body.lending-active .app-footer { display: block; }
      body.lending-active .lending-layout { grid-template-columns: 1fr; }
      .main { padding: 1rem; }
      .main-shell { min-height: calc(100vh - 2rem); }
      .card-inner { padding: 1rem; }
      .field-group.inline { grid-template-columns: 1fr; }
      .header { align-items: flex-start; flex-direction: column; }
      .size-grid { grid-template-columns: 1fr; gap: 0.75rem; }
    }
    @media (max-height: 819px) {
      html, body {
        height: auto;
        min-height: 100%;
        overflow: auto;
      }
      #app { min-height: 100vh; }
      .shell { min-height: 100vh; }
      .sidebar {
        gap: 0.625rem;
        padding: 0.875rem 0.75rem 0.75rem;
      }
      .brand {
        padding: 0.125rem 0.125rem 0.5rem;
      }
      .brand-main { gap: 0.375rem; }
      .brand-logo { max-width: 9.25rem; }
      .brand-caption { line-height: 1.35; }
      .nav-group { gap: 0.25rem; }
      .nav-btn, .nav-sub-btn, .nav-group-btn {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
      }
      .nav-group-btn { margin-top: 0.25rem; }
      .sidebar-footer {
        padding: 0.625rem 0.75rem 0.125rem;
        line-height: 1.4;
      }
      .main { padding: 1rem; }
      .main-shell { min-height: calc(100vh - 2rem); }
      body.lending-active .main { padding: 0.75rem; }
      body.lending-active .main-shell { min-height: calc(100vh - 1.5rem); }
      body.lending-active .header,
      body.lending-active .app-footer {
        display: none;
      }
      .header {
        gap: 0.75rem;
        margin-bottom: 0.75rem;
      }
      .header h2 { font-size: 1.25rem; }
      .header p { margin-top: 0.25rem; }
      .screen { gap: 0.875rem; }
      .card-inner { padding: 1rem; }
      .card-head { margin-bottom: 0.625rem; }
      .field-row {
        gap: 0.5rem;
        margin-bottom: 0.5rem;
      }
      .field-group {
        gap: 0.25rem;
        margin-bottom: 0.625rem;
      }
      .stack { gap: 10px; }
      .button-row { margin-top: 0.5rem; }
      .toolbar {
        gap: 0.5rem;
        margin-bottom: 0.625rem;
      }
      .help {
        margin-top: 6px;
        padding: 0.625rem;
        line-height: 1.45;
      }
      .table-wrap {
        min-height: 240px;
        height: clamp(240px, calc(100vh - 19rem), 420px);
        max-height: 420px;
      }
      thead th { padding: 0.5rem 0.75rem; }
      tbody td { padding: 0.625rem 0.75rem; }
      .app-footer {
        margin-top: 1rem;
        padding-top: 0.625rem;
      }
      .lending-layout {
        gap: 0.75rem;
      }
      .lending-layout .card-inner {
        padding: 0.75rem;
      }
      .lending-layout .card-head h3 {
        font-size: 0.9375rem;
      }
      .lending-layout .field-group.inline {
        grid-template-columns: 82px minmax(0, 1fr);
        margin-bottom: 0.375rem;
      }
      .lending-layout .field-row {
        gap: 0.375rem;
        margin-bottom: 0.375rem;
      }
      .lending-layout .button-row {
        margin-top: 0.25rem;
      }
      .lending-layout .help {
        display: none;
      }
      .lending-size-section {
        margin-top: 0.5rem;
      }
      .lending-layout .size-grid {
        grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
        gap: 6px 10px;
      }
      .lending-layout .size-row {
        grid-template-columns: 20px minmax(0, 1fr);
      }
      .lending-layout .field-control.compact {
        min-height: 30px;
        padding: 0.25rem 0.5rem;
      }
      .lending-layout .mini-readout {
        min-height: 30px;
        padding: 0.25rem 0.5rem;
      }
      .lending-layout .btn {
        min-height: 32px;
        padding: 0.25rem 0.75rem;
      }
      .lending-layout .table-wrap {
        min-height: 200px;
        height: clamp(200px, calc(100vh - 20rem), 390px);
        max-height: 390px;
      }
      .modal-backdrop { padding: 12px; }
      .modal { max-height: calc(100vh - 24px); }
      .busy-overlay, .dialog-overlay { padding: 16px; }
      .busy-card, .dialog-card { padding: 18px 20px; }
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
      const title = state.screenTitles[state.currentScreen];
      const screenClass = `screen ${state.currentScreen}-screen`;
      const app = document.getElementById("app");
      document.body.classList.toggle("lending-active", state.currentScreen === "lending");
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
              <div class="sidebar-footer">
                <div>DB: ${escapeHtml(state.databaseBackend || "")}</div>
                <div>起動日: ${escapeHtml(state.currentDate || "")}</div>
              </div>
            </aside>
            <main class="main">
              <div class="main-shell">
                <div class="header">
                  <div>
                    <h2 id="screen-title">${escapeHtml(title.title)}</h2>
                    <p id="screen-subtitle">${escapeHtml(title.subtitle)}</p>
                  </div>
                </div>
                <div class="${screenClass}" id="screen-root">${renderCurrentScreen()}</div>
                <footer class="app-footer">© ARAISEIMITSU 2026 - Created By DIP Department</footer>
              </div>
            </main>
          </div>
        `;
        state.shellRendered = true;
      } else {
        const titleNode = document.getElementById("screen-title");
        const subtitleNode = document.getElementById("screen-subtitle");
        const screenRoot = document.getElementById("screen-root");
        const sidebar = document.querySelector(".sidebar");
        const navButtons = Array.from(document.querySelectorAll("[data-action=\"navigate\"]"));
        const masterButton = document.querySelector("[data-action=\"toggle-master\"]");
        const sidebarToggle = document.querySelector("[data-action=\"toggle-sidebar\"]");
        const subList = document.querySelector(".nav-sub-list");
        if (titleNode) titleNode.textContent = title.title;
        if (subtitleNode) subtitleNode.textContent = title.subtitle;
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
                <div class="button-row" style="margin:0;">
                  <button class="btn secondary small" data-action="confirmation-refresh">再読込</button>
                  <button class="btn danger small" data-action="confirmation-delete-batch" ${s.selectedBatchMachineCode ? "" : "disabled"}>削除</button>
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

    function renderBatchTable(rows, selectedMachineCode, selectedReturnedOn) {
      if (!rows || !rows.length) {
        return '<div class="empty-state">確認済みバッチはありません。</div>';
      }
      const head = '<tr><th>機番</th><th>返却日</th></tr>';
      const body = rows.map((row, index) => {
        const selected = String(selectedMachineCode ?? "") === String(row.machine_code ?? "")
          && String(selectedReturnedOn ?? "") === String(row.returned_on ?? "");
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

    function extractCaseNo(machineCode) {
      const normalized = String(machineCode || "").trim();
      if (!normalized.includes("-")) return "";
      return normalized.slice(normalized.indexOf("-") + 1).trim();
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
        const nextScreen = target.dataset.screen;
        state.currentScreen = nextScreen;
        renderApp();
        if (nextScreen === "confirmation") {
          await refreshConfirmationBatches();
        }
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
        const caseNo = extractCaseNo(row.machine_code || "");
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
            if (!(await confirmDialog("単票返却", "選択した 1 件を返却しますか？"))) return;
            setBusy("単票返却", "返却処理を実行しています...");
            await invokeApi("return_one_loan", {
              loan_id: state.return.selectedLoanId,
              case_no: state.return.caseNo,
              returned_on: state.return.date,
            });
            await refreshReturnSearch();
            await refreshConfirmationBatches();
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
          case "confirmation-delete-batch":
            if (!state.confirmation.selectedBatchMachineCode) return;
            if (!(await confirmDialog("確認済バッチ削除", `${state.confirmation.selectedBatchMachineCode} の確認待ちデータを削除しますか？`))) return;
            setBusy("確認済バッチ削除", "確認待ちデータを削除しています...");
            {
              const data = await invokeApi("delete_confirmation_batch", {
                machine_code: state.confirmation.selectedBatchMachineCode,
                returned_on: state.confirmation.selectedBatchReturnedOn || null,
              });
              state.confirmation.caseNo = "";
              state.confirmation.detailLoans = [];
              state.confirmation.selectedLoanId = null;
              state.confirmation.selectedBatchMachineCode = "";
              state.confirmation.selectedBatchReturnedOn = "";
              await refreshConfirmationBatches();
              toast("完了", `${data.count || 0}件を削除しました。`);
            }
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
  </script>
</body>
</html>
"""
