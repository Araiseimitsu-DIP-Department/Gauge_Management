# 現行構成

Windows向けピンゲージの貸出・返却・確認・マスタ管理アプリ。
Python 3.12、pywebview 5系、Windows Forms / Edge WebView2を使用する。

## 起動とデータ経路

`main.py` → `app/bootstrap.py` → 設定読込・repository選択・service構築 → pywebview画面。
画面は `app/webview/frontend.py` のHTML/CSS/JavaScript、Pythonとの入口は `backend.py` の `WebviewBridge`。
処理は bridge → services → application/usecases → repository port → infrastructure実装。
models、DTO、mappers、共通エラーは両DBで共有する。
`app/repositories` には旧Access実装と、現在も共有される `errors.py`・`ports.py` がある。ディレクトリ単位で除外しない。

## 外部連携・設定

確認できる接続先はPostgreSQLまたはAccess。外部HTTP APIサービスの実装は確認していない。
DB切替・設定読込は `config/app_settings.py`、`config/db_settings.py`、`utils/env_loader.py`。
環境変数名のキーを持つ設定ファイルを読む実装であり、OS環境変数を直接読み込む方式ではない。
設定キーとセットアップはREADME、ビルド構成は [BUILD.md](BUILD.md) を参照。
`docs/` のAccessフォーム・VBA・メタ情報は移行元の資料。`scripts/` と `database/postgresql/` は移行用。

## 人間確認が必要な点

実際の配布先Windows構成、リリース承認者、バックアップ保管方針はコードから確定できない。
GUIスモーク確認と本番DBに関する操作は、データ更新の可能性を確認して実施する。
