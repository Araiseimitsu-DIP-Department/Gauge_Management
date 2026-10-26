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
- ライト／ダークモード切替（Windowsユーザーごとに保存）

## バージョン管理

現在のバージョンは **v1.2.1** です。画面下部のフッターに、小文字の `v` を付けて表示します。
検討中の細かな修正ごとにはバージョンを進めず、公開する更新単位で `app/version.py` の `APP_VERSION` を更新します。
互換性を保つ機能追加はMINOR、不具合修正・既存機能の表示改善はPATCH、互換性のない変更はMAJORを更新し、重要な変更を `docs/update.md` に記録します。

## 画面運用メモ

- アプリを開いたまま日付が変わると、貸出日・返却日をPCの今日の日付へ自動更新します（30秒ごと、画面復帰時、操作時に確認）。他の入力内容・選択・一覧は保持します。同じ日内では手動指定した日付を維持し、日付が変わった時点で今日へ切り替えます。履歴の編集画面の日付とサイドバーの起動日は変更しません。
- 返却・確認の対象一覧は高さに収まる間は1列で表示し、収まらず横幅を確保できる場合に左右2列へ切り替えます。ウィンドウのサイズ変更にも追従します。2列の場合は左列を上から下へ読み、続きは右列の上から下へ進みます（25件なら左13件・右12件）。個別操作は選択した1件、一括操作は対象全件に適用します。
- 返却・確認の対象一覧では、サイズを太字で強調します。1列・2列表示、ライト・ダークの両モードで共通です。
- 各ページの冒頭に表示していたメインタイトルと補足文は非表示にし、操作カードから表示を開始します。
- 貸出登録のサイズ入力は 1～10、11～20、21～30 の縦3列表示です。自動フォーカス移動は番号順に進みます。
- 貸出登録では、機番左、機番右、担当者、サイズ1の順に自動フォーカス移動します。
- 返却画面では、返却日・返却ケースNo・選択中サイズ・個別返却・一括返却を一行にまとめ、ボタンは入力欄のすぐ右へ配置しています。機番検索・クリアも機番欄のすぐ右に配置します。
- 返却画面はPG表との左右比較に対応し、1366px画面の半分幅（約683px）・2/3幅（約911px）でも利用できます。幅1150px以下ではサイドバーを自動でアイコン表示にし、広げると元の表示に戻します。一覧の列順は「サイズ・ケースNo・担当者・機番・貸出日」です。
- 貸出画面は登録・一覧を左右50%ずつの均等幅で配置し、30件のサイズ入力を縦10行×3列で維持します。一覧はサイズを先頭に表示し、検索モードに対応する条件だけを表示します。入力内容とEnterキーの移動順は維持します。
- PG・担当者マスタは検索欄を一覧見出しの下へ集約し、編集欄の幅を抑えます。幅1050px以下では一覧と編集欄を上下に配置し、一覧内スクロールと保存操作を一画面で利用できます。貸出・マスタ管理でも幅1150px以下はサイドバーを自動でアイコン表示にします。
- 返却ケースNoは半角数字1～2桁のみ登録できます。未入力、英字やハイフンを含む値（F8、F-8など）、全角数字はエラー表示し、個別返却と一括返却を実行できません。既存データを検索する確認画面の入力条件は維持します。
- 個別返却後は返却ケースNoを保持し、クリアボタンと一括返却後は返却ケースNoをクリアします。
- 確認画面では、確認対象を選択すると選択中サイズを表示し、個別確認を実行できます。
- 確認済みバッチ一覧は返却ケースNoと返却日を表示します。Access版に合わせ、確認済みバッチの削除ボタンは表示していません。

## 動作環境

- Windows
- Python 3.12 系
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

初回セットアップ（PostgreSQL運用）:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` の `POSTGRES_CONNECTION_URL`（または `DATABASE_URL`）に接続先を設定します。
Accessへ戻す場合は `requirements-access.txt` をインストールし、`DB_BACKEND=access` と `ACCESS_DB_DIRECTORY` を設定します。
設定はファイルから読み込みます。現在のアプリは同名のOS環境変数を読み込みません。

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
| 貸出ID | `pin_gauge_lending.id`（DBシーケンスによる自動採番。新規DDLはIDENTITY、現在のDBはDEFAULT nextval構成） |

貸出新規登録（PostgreSQL）では `id` を INSERT 文に含めず、シーケンス `pin_gauge_lending_id_seq` による自動採番に任せます。登録後の一覧表示は、従来どおり貸出日・機番・担当者で再取得します。
IDを明示する移行・不足行追記後は採番値の整合確認が必要です。調査結果、補正手順、再発防止は `docs/loan-sequence.md` を参照してください。

## PostgreSQL 移行

移行手順は `docs/postgresql-migration.md` にまとめています。
移行ツールはAccessを読み取るため、実行環境に `requirements-access.txt` とAccess ODBCドライバーが必要です。

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

通常ビルドはPostgreSQL専用です。`.env` から選択DBに必要な設定だけを生成して同梱し、`DESIGN/arai_logo.png`、Windows GUI依存、PostgreSQLドライバーを維持します。
Accessコード、`pyodbc`、Access接続設定、移行用資料・DBファイルは通常の成果物に含めません。
接続先やパスワードは従来どおりexe内に格納されるため、成果物と `build/config/` は適切に管理してください。
同梱設定を優先する既存の読込順は維持します。exe横の `.env` で同梱設定を上書きすることはできません。

Access用ビルドは `.env` をAccess設定にしてから、明示的に指定します。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-access.txt
$env:PINGAUGE_BUILD_BACKEND='access'
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm PinGaugeMgmt.spec
Remove-Item Env:PINGAUGE_BUILD_BACKEND
```

ビルド種別と `.env` の `DB_BACKEND` が一致しなければビルドを停止します。復帰手順と検証は `docs/BUILD.md` を参照してください。

## 開発・検証

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

AI開発の参照先は `AGENTS.md`、検証・承認条件は `.agents/skills/development-workflow/SKILL.md` です。

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

- アプリの最小ウィンドウサイズは `680x680` です。
- 1366x768・表示スケール100%を基準に、サイドバー、余白、入力欄、表の行間を圧縮しています。タイトルバー・タスクバーを差し引いた高さ680pxの表示領域でも、操作欄・サイズ入力30件・フッターを一画面で確認できます。
- 貸出画面は登録と一覧、確認画面は対象と確認済みバッチを左右に配置します。確認対象の長いケースNo・担当者名はセル内で折り返し、件数が多い場合は一覧内をスクロールします。横幅に収まらない場合も一覧内の横スクロールで全文を確認できます。
- 確認対象一覧は14～16pxの文字で表示し、1列に並べた実際の高さと一覧領域の高さを比較して列数を決めます。左右2列にしても高さに収まらない場合は一覧内でスクロールします。確認済みバッチは右端のパネルに表示します。返却対象一覧は12pxの文字・約25pxの行高を維持します。
- 対象一覧は2列分の幅を確保できない場合（返却は一覧幅896px未満、確認は816px未満）、1列でスクロールします。元の並び順・操作対象は維持します。返却画面は狭い幅でも入力と操作欄を上部に残し、一覧内をスクロールします。
- ウィンドウの幅900px以下または高さ560px以下では縦配置に切り替え、画面全体のスクロールで各操作に到達できるようにします。
- 貸出は幅1050px以下で登録・一覧を上下に配置し、画面内をスクロールして利用します。PG・担当者マスタは同じ幅で上下配置にし、通常の高さでは編集欄を表示したまま一覧内をスクロールします。狭い幅でもPG・担当者マスタの切替アイコンを利用できます。
- サイドバー下部の「ダークモードに切替」「ライトモードに切替」で表示を変更します。サイドバーを折りたたんだ場合も月／太陽ボタンで切替できます。
- 設定は `%LOCALAPPDATA%\PinGaugeMgmt\ui-theme.txt` に保存し、次回起動時に反映します。未保存・不正な設定の場合はライトモードになります。保存できない場合はエラーを表示し、その起動中の切替は維持します。業務DBの更新や追加の環境変数設定は不要です。
