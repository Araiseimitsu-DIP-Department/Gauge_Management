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
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder\ピンゲージ管理DB.accdb
```

現在の標準ファイル名は `ピンゲージ管理DB.accdb` です。

```env
APP_ENV=local
ACCESS_DB_DIRECTORY=\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb
```

フォルダを指定した場合、アプリは最終的に `ピンゲージ管理DB.accdb` を接続対象として扱います。

## PostgreSQL 設定

```env
APP_ENV=local
DB_BACKEND=postgres
POSTGRES_CONNECTION_URL=postgresql://postgres:password@192.168.1.120:5432/pingauge_management_db
DATABASE_URL=postgresql://postgres:password@192.168.1.120:5432/pingauge_management_db
POSTGRES_SCHEMA=public
```

`POSTGRES_CONNECTION_URL` を優先します。`DATABASE_URL` は移行ツール互換用で、`POSTGRES_CONNECTION_URL` が未設定の場合にも利用できます。

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
