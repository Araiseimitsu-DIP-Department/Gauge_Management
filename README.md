# ピンゲージ管理

Windows 業務 PC 向けの `Python + PySide6` デスクトップアプリです。  
既存の Access データベース `ピンゲージ管理.accdb` を利用し、ピンゲージの `貸出`、`返却`、`確認`、`PGマスタ管理`、`担当者マスタ管理` を行います。

内部構成は `presentation / application / domain / infrastructure / shared` に分離し、将来的な PostgreSQL 移行を前提にしています。  
現在は `DB_BACKEND=access` を既定にして、既存の Access 運用を維持したまま PostgreSQL へ切り替えやすい形に整えています。

## 主な機能

- 貸出登録
  - 日付、機番、担当者、サイズ 1〜20 件をまとめて登録
  - 貸出一覧検索
  - 貸出データの修正・削除
- 返却処理
  - 機番ごとの返却対象検索
  - 個別返却
  - 一括返却
- 確認処理
  - 返却ケース No による確認対象検索
  - 個別確認
  - 一括確認
  - 確認待ち一覧からの対象呼び出し
- マスタ管理
  - PGマスタの検索、登録、更新、削除
  - 担当者マスタの検索、更新
- 共通 UI
  - 入力確認ダイアログ
  - DB 処理中のスピナー表示

## 前提環境

- Windows
- Python 3.12 系
- Access を参照できる `pyodbc` 実行環境
- 接続対象の Access ファイル
  - ファイル名は `ピンゲージ管理.accdb`
- PostgreSQL に切り替える場合は `psycopg` 系ドライバを追加

## セットアップ

依存関係をインストールします。

```powershell
pip install -r requirements.txt
```

プロジェクトルートに `.env` を作成し、Access ファイルの保存先を設定します。  
`ACCESS_DB_DIRECTORY` には `フォルダ` でも `accdb のフルパス` でも指定できます。

```env
APP_ENV=local
APP_NAME=ピンゲージ管理
DB_BACKEND=access
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder
```

または:

```env
APP_ENV=local
APP_NAME=ピンゲージ管理
DB_BACKEND=access
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder\ピンゲージ管理.accdb
```

PostgreSQL に切り替える場合は以下を追加します。

```env
DB_BACKEND=postgres
POSTGRES_CONNECTION_URL=postgresql://user:password@localhost:5432/pingauge
POSTGRES_SCHEMA=public
```

補足は [docs/SETUP.md](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/docs/SETUP.md) を参照してください。

## 起動方法

推奨の起動入口はルートの `main.py` です。

```powershell
python main.py
```

## 配布ビルド

配布用 exe は `PinGaugeMgmt.spec` を使って生成します。  
アイコンは `docs/精密計測具のアイコン.png` を使用します。

```powershell
pyinstaller PinGaugeMgmt.spec
```

生成物は `dist/ピンゲージ管理.exe` です。

## フォルダ構成

```text
Gauge_Management/
├─ app/
│  ├─ bootstrap.py            アプリ起動初期化
│  ├─ config/                 設定読込、DB 接続設定
│  ├─ models/                 既存の業務データモデル
│  ├─ shared/                 共通例外、共通ユーティリティ
│  ├─ domain/                 業務概念モデル、値オブジェクト
│  ├─ application/            DTO、Repository port、usecase
│  ├─ infrastructure/         Access 実装、PostgreSQL 実装、接続、mapper
│  ├─ services/               UI 向けファサード
│  ├─ ui/
│  │  ├─ main_window.py       メインウィンドウ、サイドバー
│  │  ├─ screens/             貸出、返却、確認、マスタ画面
│  │  ├─ dialogs/             貸出修正ダイアログ
│  │  ├─ widgets/             共通部品、確認ダイアログ、日付入力、スピナー
│  │  └─ styles/              スタイル定義、SVG アセット
│  └─ utils/                  入力検証、例外、.env 読込
├─ docs/                      業務仕様、デザイン案、セットアップ資料
├─ tests/                     テスト用補助ファイル
├─ .env.example               環境変数サンプル
├─ PinGaugeMgmt.spec          PyInstaller 配布定義
├─ requirements.txt           依存関係
└─ main.py                    推奨起動入口
```

## 主なファイル

- [main.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/main.py)
  - 推奨のアプリ起動入口
- [app/bootstrap.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/bootstrap.py)
  - `QApplication` 初期化とメインウィンドウ起動
- [app/config/app_settings.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/config/app_settings.py)
  - アプリ設定読込
- [app/config/db_settings.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/config/db_settings.py)
  - Access / PostgreSQL の接続設定
- [app/infrastructure/repository_factory.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/infrastructure/repository_factory.py)
  - `DB_BACKEND` に応じた repository 切替
- [app/ui/main_window.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/ui/main_window.py)
  - サイドバーと各画面の切替
- [app/ui/widgets/busy_indicator.py](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/app/ui/widgets/busy_indicator.py)
  - 処理待ちスピナー

## 画面一覧

- 貸出
- 返却
- 確認
- マスタ管理
  - PGマスタ
  - 担当者マスタ

## 開発メモ

- 画面イベントに SQL を直接書かず、`ui -> services -> application/usecases -> infrastructure` を通す構成です。
- Access の実データを使うため、DB スキーマ変更は慎重に扱ってください。
- Access 固有の実装は `app/infrastructure/access/` に寄せ、PostgreSQL 実装は `app/infrastructure/postgres/` に置く前提です。
- `app/infrastructure/repository_factory.py` が `DB_BACKEND` を見て Access / PostgreSQL を切り替えます。
- PostgreSQL 側はまだ骨格段階なので、`DB_BACKEND=postgres` に切り替える前に依存パッケージと接続先を用意してください。
- 生成物は `.gitignore` で除外していますが、`__pycache__` などはローカルで再生成されます。
- 既存の業務仕様は [docs/Gauge_Management.txt](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/docs/Gauge_Management.txt) を基準にしています。
