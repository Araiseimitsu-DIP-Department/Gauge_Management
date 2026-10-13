# 検証結果

本書は初回のビルド最適化時点の検証記録です。その後の貸出登録不具合の調査・DB補正・追加テスト31件の結果は [loan-sequence.md](loan-sequence.md) を参照してください。

2026-10-13、Windows / Python 3.12.10 / PyInstaller 6.20.0環境で実施。

| 項目 | 結果 |
|---|---|
| Tests | PASS: unittest 19件。実DB更新なし |
| Access不在起動 | PASS: 別PythonプロセスでAccess/pyodbcインポートを禁止し、GUI呼出を模擬してbootstrap.runまで実行 |
| ビルド | PASS: 通常権限のWindows環境でonefileを再ビルド |
| 収録物 | PASS: exe内のPYZとDLL・データ一覧を検査。Access実装・pyodbc/pypyodbc・ODBC・DB/VBA/SQLファイル不在 |
| 必要依存 | PASS: psycopg/psycopg_binary/libpq、webview/pythonnet/clr_loader、ロゴ維持 |
| 設定 | PASS: DB_BACKEND=postgresと許可した設定キーだけを同梱。接続の実値は非公開 |
| PostgreSQL接続 | PASS: 読取専用トランザクションのSELECT 1、3テーブルの件数確認 |
| 既存repository | PASS: 全接続を読取専用にして担当者・PGマスタ・貸出・確認一覧・返却対象を取得 |
| review-code / code-simplifier | 実施: 目的外変更なし。テスト用子プロセス呼出を共通化し、Windows日本語ログの文字コードを統一。既存Tests全件PASS |
| ハーネス | PASS: Skills 7件のfrontmatter、参照Docs・共通手順の存在、責務分離を確認 |
| Git Diff / Status | 確認済み。diff --check PASS。Access実装とPostgreSQL接続・SQLに差分なし |
| lint / 型チェック | NOT RUN: 既存設定・コマンドなし |
| exe実画面・実DB更新 | NOT RUN: GUI初期化は部署UPDATEを含むため、実DB設定で起動していない |
| Accessの接続・exe | NOT RUN: ソースでの明示選択とビルド設定のテストのみ |
| Release Ready | NO: 配布先WindowsでのGUI確認と隔離検証DBでの更新機能確認が残る |

読取時点の件数: pin_gauge_master 2,031件、staff_master 29件、pin_gauge_lending 32,522件。
過去の移行履歴の件数とは異なる。今回データの変更・補正・再移行はしていない。

## サイズ比較

旧exe 15,635,306 bytes、新exe 16,591,652 bytes、差 +956,346 bytes（+6.12%）。
旧成果物のpyodbc拡張は圧縮状態で59,149 bytesあり、新成果物には存在しない。
一方、旧成果物にないWindowsランタイムDLL 43件が追加され、圧縮合計1,030,219 bytes。
旧成果物のビルド環境は完全には確定できないため、サイズ差をAccess除外単独の効果とは扱わない。
互換性を優先し、用途不明のDLLを推測で削除していない。

## 変更ファイルと保持範囲

- アプリ: `app/infrastructure/repository_factory.py`、`app/config/app_settings.py`。
- ビルド・依存・設定: `PinGaugeMgmt.spec`、`requirements.txt`、`requirements-access.txt`、`.env.example`。
- ハーネス: `AGENTS.md`、`.cursor/rules/development.mdc`・`safety.mdc`、`.agents/skills/` のdevelopment-workflow・implement-feature・fix-bug・review-code・release・datasource-build・code-simplifier。
- 共通手順: development-workflow/referencesのdata-update-verification.md、learning-feedback.md。
- Docs: `README.md`、`docs/SETUP.md`、`ARCHITECTURE.md`、`BUSINESS_RULES.md`、`DATABASE.md`、`BUILD.md`、`HARNESS.md`、本書、`update.md`。
- Tests: `tests/README.md`、`test_backend_build.py`、`test_business_rules.py`。

Accessのrepository・mapper・接続補助、旧repository、移行スクリプト・VBA資料を保持。
PostgreSQLの接続・repository・SQL、既存業務処理は変更していない。
既存の同梱設定優先順を維持しているため、exe横の.envで同梱設定を上書きできない。
接続設定を含む成果物とbuild/configは従来と同様に適切なアクセス管理が必要。

成果物は `dist/ピンゲージ管理.exe`（同一内容を `dist/postgres/` にも保存）。
旧exeは `dist/before-postgres-20261013/ピンゲージ管理.exe` に退避。

## 次の確認

隔離された検証DBを用意し、配布先相当のWindowsで画面表示、貸出・返却・確認・マスタ更新を検証する。
本番への配布・DB更新は今回実行していない。
