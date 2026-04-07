# Setup

## Access 設定

プロジェクトルートに `.env` を作成してください。
`.env` が無い場合は `.env.example` を参照します。

```env
APP_ENV=local
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder
```

次の形式も使えます。

```env
APP_ENV=local
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder\ピンゲージ管理.accdb
```

アプリは最終的に `ピンゲージ管理.accdb` を接続対象として扱います。

## Run

```powershell
python main.py
```

## Structure

```text
app/
  config/        Configuration loading and Access path settings
  models/        Business models
  repositories/  Access and data access layer
  services/      Business logic
  ui/            PySide6 windows, screens, widgets, dialogs
  utils/         Shared helpers
tests/           Tests
docs/            Design and business source documents
```
