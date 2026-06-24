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

## 画面運用メモ

- 貸出登録のサイズ入力は 1～10、11～20、21～30 の縦3列表示です。自動フォーカス移動は番号順に進みます。
- 貸出登録では、機番左、機番右、担当者、サイズ1の順に自動フォーカス移動します。
- 返却画面では、返却日、返却ケースNo、選択中サイズ、個別返却、一括返却を返却対象一覧側に集約しています。
- 返却ケースNo未入力時は、個別返却と一括返却を実行できません。
- 個別返却後は返却ケースNoを保持し、クリアボタンと一括返却後は返却ケースNoをクリアします。
- 確認画面では、確認対象を選択すると選択中サイズを表示し、個別確認を実行できます。
- 確認済みバッチ一覧は返却ケースNoと返却日を表示します。Access版に合わせ、確認済みバッチの削除ボタンは表示していません。

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
    app_icon.png                 アプリ用アイコン（元画像）
    app_icon.ico                 PyInstaller 用のアイコン
    SETUP.md                     初期設定メモ
    DESIGN.md                    画面・見た目の整理メモ
    postgresql-migration.md      Access -> PostgreSQL 移行手順書
  DESIGN/
    DESIGN.md                    現行 UI デザインガイド
    arai_logo.png                サイドバー表示用ロゴ
    arai_logo_wt.png             ロゴ白版
    arai_site.jpg                参考イメージ
  database/
    postgresql/                  PostgreSQL DDL、検証SQL、移行メモ
  scripts/
    migrate_access_to_postgres.py Access から PostgreSQL への移行スクリプト
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
.\.venv\Scripts\python.exe main.py
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
POSTGRES_CONNECTION_URL=postgresql://user:password@192.168.1.120:5432/pingauge_management_db
DATABASE_URL=postgresql://user:password@192.168.1.120:5432/pingauge_management_db
POSTGRES_SCHEMA=public
```

`DATABASE_URL` は `docs/pingauge_management_db` の移行ツール互換用です。アプリは `POSTGRES_CONNECTION_URL` を優先し、未設定の場合は `DATABASE_URL` も読み込みます。

PostgreSQL 側の物理名は英語表記です。Access のクエリは PostgreSQL ビューにはせず、アプリの Python repository 層で JOIN / 条件処理します。

| Access | PostgreSQL |
|---|---|
| `t_PGマスタ` | `pin_gauge_master` |
| `t_担当者マスタ` | `staff_master` |
| `t_貸出` | `pin_gauge_lending` |

主なカラム対応:

| 用途 | PostgreSQL |
|---|---|
| 保有数 | `pin_gauge_master.owned_quantity` |
| 表示フラグ | `staff_master.display_flag` |
| 機番 | `pin_gauge_lending.machine_no` |
| 貸出日 / 返却日 | `pin_gauge_lending.lent_date` / `pin_gauge_lending.returned_date` |

## PostgreSQL 移行

移行手順は `docs/postgresql-migration.md` にまとめています。

事前確認のみ:

```powershell
.\.venv\Scripts\python.exe scripts\migrate_access_to_postgres.py --dry-run
```

本投入:

```powershell
.\.venv\Scripts\python.exe scripts\migrate_access_to_postgres.py --apply-schema --truncate
```

`--truncate` を付けると、PostgreSQL の `pin_gauge_lending`、`pin_gauge_master`、`staff_master` を全削除してから Access のデータを投入します。テストデータを含む既存データを置き換える場合に使用します。

投入後は `database/postgresql/020_validation.sql` で検証します。制約は `database/postgresql/003_constraints.sql` で管理しています。

### 直近の移行結果

2026-06-24 に Access から PostgreSQL へ再取込を実施しました。

| テーブル | 件数 |
|---|---:|
| `pin_gauge_master` | 2333 |
| `staff_master` | 29 |
| `pin_gauge_lending` | 32478 |

`pin_gauge_master` は Access 元データ 2030 件に加え、貸出履歴に存在してマスタにないサイズ 303 件をプレースホルダとして補完しています。

## onefile ビルド

PyInstaller で 1 ファイル版の exe を作成します。

ビルド環境には `pyinstaller` と `Pillow` が必要です。

```powershell
pyinstaller PinGaugeMgmt.spec
```

成果物は `dist/ピンゲージ管理.exe` です。

`PinGaugeMgmt.spec` では `.env` に加えて `DESIGN/arai_logo.png` も同梱しており、ビルド後のサイドバーでもロゴ画像が表示されます。

## アイコン

- アプリの元画像は `docs/app_icon.png`
- ビルド用の Windows アイコンは `docs/app_icon.ico`
- タスクバーや exe のアイコンは PyInstaller の `icon` 指定で反映します

## 補足

- 旧 PySide6 GUI は廃止し、現在は `app/webview` が GUI 本体です
- `DESIGN/DESIGN.md` を優先参照し、業務ロジックを変えずに UI デザインを調整する運用です
- UI 更新時のチラつきを抑えるため、画面の全面再描画を減らしています
- DB 処理は `application -> services -> infrastructure` の流れで実行しています
- PGマスタは、貸出履歴で使用中のサイズを削除しようとした場合、参照件数を表示して削除を止めます

## 低解像度・表示スケール環境

- アプリの最小ウィンドウサイズは `1100x680` です。
- 1366x768、1280x720、Windows 表示スケール 125% / 150% 相当の低い表示領域では、画面全体を縦スクロールできるようにしています。
- 一覧は `.table-wrap` 内でスクロールし、低い画面でも最低限の高さを確保します。下部の操作ボタンやフッターへ届かない場合は、アプリ全体の縦スクロールで到達できます。
- 高さに余裕がある画面では、従来どおりサイドバー、入力パネル、一覧の固定気味レイアウトと一覧内部スクロールを優先します。
