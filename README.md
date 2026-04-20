# ピンゲージ管理

ピンゲージ管理は、貸出、返却、確認、PGマスタ、担当者マスタを扱う Windows 向けの業務アプリです。

現在の GUI は `pywebview` ベースで実装しており、処理本体は既存の service / usecase / repository 構成をそのまま利用しています。

## 主な機能

- 貸出登録
- 貸出一覧の検索、編集、削除
- 返却処理
- 返却済みデータの確認処理
- PGマスタの検索、編集、削除
- 担当者マスタの検索、編集

## 動作環境

- Windows
- Python 3.12 系
- `pyodbc` が利用できる環境
- Access バックエンドを使う場合は Microsoft Access Database Engine または Access ODBC ドライバが必要
- PostgreSQL バックエンドを使う場合は `psycopg` と接続先が必要

## 現在の構成

```text
Gauge_Management/
  app/
    bootstrap.py                 アプリ起動と pywebview ウィンドウ生成
    config/                      環境変数と DB 設定
    application/                 usecase と repository port
    domain/                      ドメインモデル
    infrastructure/              Access / PostgreSQL 実装
    repositories/                接続補助と共通 repository 層
    services/                    画面向けサービス層
    shared/                      共通 Result / Error
    utils/                       環境変数読込、バリデーション
    webview/                     HTML / CSS / JavaScript の GUI 実装
  docs/
    精密計測具のアイコン.png     元のアイコン画像
    pingauge.ico                 PyInstaller 用のアイコン
    SETUP.md                     初期設定メモ
    DESIGN.md                    画面・見た目の整理メモ
  tests/
    README.md
  main.py                        ルート起動ファイル
  PinGaugeMgmt.spec              PyInstaller onefile 用定義
  requirements.txt               実行時依存
```

## 起動

`.env` がある場合は、それを優先して読み込みます。
`.env` がなくてもアプリ自体は起動し、DB 未設定の場合は操作時にエラーを表示します。

```powershell
python main.py
```

## 設定

### Access を使う場合

```env
APP_ENV=local
APP_NAME=ピンゲージ管理
DB_BACKEND=access
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder
```

`ACCESS_DB_DIRECTORY` には Access の `.accdb` が入っているフォルダ、または `.accdb` ファイルのフルパスを指定できます。

### PostgreSQL を使う場合

```env
APP_ENV=local
APP_NAME=ピンゲージ管理
DB_BACKEND=postgres
POSTGRES_CONNECTION_URL=postgresql://user:password@localhost:5432/pingauge
POSTGRES_SCHEMA=public
```

## onefile ビルド

PyInstaller で 1 ファイル版の exe を作成します。

ビルド環境には `pyinstaller` と `Pillow` が必要です。

```powershell
pyinstaller PinGaugeMgmt.spec
```

成果物は `dist/ピンゲージ管理.exe` です。

## アイコン

- アプリの元画像は `docs/精密計測具のアイコン.png`
- ビルド用の Windows アイコンは `docs/pingauge.ico`
- タスクバーや exe のアイコンは PyInstaller の `icon` 指定で反映します

## 補足

- 旧 PySide6 GUI は廃止し、現在は `app/webview` が GUI 本体です
- UI 更新時のチラつきを抑えるため、画面の全面再描画を減らしています
- DB 処理は `application -> services -> infrastructure` の流れで実行しています
