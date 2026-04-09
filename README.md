# ピンゲージ管理

Windows 業務 PC 向けの `Python + PySide6` デスクトップアプリです。  
既存の Access データベース `ピンゲージ管理.accdb` を利用し、ピンゲージの `貸出`、`返却`、`確認`、`PGマスタ管理`、`担当者マスタ管理` を行います。

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

## セットアップ

依存関係をインストールします。

```powershell
pip install -r requirements.txt
```

プロジェクトルートに `.env` を作成し、Access ファイルの保存先を設定します。  
`ACCESS_DB_DIRECTORY` には `フォルダ` でも `accdb のフルパス` でも指定できます。

```env
APP_ENV=local
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder
```

または

```env
APP_ENV=local
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder\ピンゲージ管理.accdb
```

補足は [docs/SETUP.md](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/docs/SETUP.md) を参照してください。

## 起動方法

推奨の起動入口はルートの `main.py` です。

```powershell
python main.py
```

## アイコン

- アプリアイコン（実行時・配布元画像）
  - [docs/icon.png](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/docs/icon.png)

アプリ起動時は `app/bootstrap.py` で上記 PNG を読み込み、ウィンドウアイコンに設定しています。  
`onefile` で exe 化する場合は、`--icon` で exe のアイコンを指定し、実行時も同じ画像を使うため `--add-data` で `docs` 配下へ同梱してください。PNG をそのまま指定できない PyInstaller の場合は `.ico` に変換して `--icon` に指定してください。

```powershell
pyinstaller --onefile --windowed --icon docs/icon.png --add-data "docs/icon.png;docs" --name "ピンゲージ管理" main.py
```

生成物は `dist/ピンゲージ管理.exe` です。

## フォルダ構成

```text
Gauge_Management/
├─ app/
│  ├─ main.py                 app 直下から実行する場合の入口
│  ├─ bootstrap.py            アプリ起動初期化
│  ├─ config/                 設定読込、Access 接続設定
│  ├─ models/                 業務データモデル
│  ├─ repositories/           Access データアクセス層
│  ├─ services/               業務ロジック層
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
  - Access パス解決と接続設定
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

- 画面イベントに SQL を直接書かず、`services -> repositories` を通す構成です。
- Access の実データを使うため、DB スキーマ変更は慎重に扱ってください。
- 生成物は `.gitignore` で除外していますが、`__pycache__` などはローカルで再生成されます。
- 既存の業務仕様は [docs/Gauge_Management.txt](/c:/Users/SEIZOU-20/PycharmProjects/Gauge_Management/docs/Gauge_Management.txt) を基準にしています。
