# ビルド構成

## 依存関係の分類

| 分類 | 対象 | 通常のPostgreSQLビルド |
|---|---|---|
| Access専用 | pyodbc、旧Access repository、Access mappers・接続補助 | 除外。Pythonソースは保持 |
| 未使用 | pypyodbc | 除外 |
| 調査で使用箇所なし | win32com | 安易なWindows共通依存除外を避け、明示除外しない |
| PostgreSQL | psycopg、psycopg_binary、libpqと依存DLL | 維持 |
| GUI共通 | pywebview、pythonnet、CLR、Windows Forms、Edge WebView2 | 維持 |
| アプリ共通 | models、DTO、port、service、usecase、errors、validators | 維持 |
| 資料・移行専用 | scripts、SQL、VBA、Accessメタ資料、accdb/mdb、ODBCインストーラー | データ同梱指定なし |

`PinGaugeMgmt.spec` はPyInstaller onefile構成を維持する。
ビルド用OS環境変数 `PINGAUGE_BUILD_BACKEND` は未指定時 `postgres`、復帰時は `access`。
Accessに戻す場合もPostgreSQL共通依存は削除せず維持する。
`.env` の選択値とビルド種別が不一致ならエラー。データファイルは選択DBの設定とロゴのみ。
通常はAPP_ENV、APP_NAME、DB_BACKEND、PostgreSQLのURL2種・SCHEMAを同梱する。
Access版ではURL・SCHEMAを同梱せず、ACCESS_DB_DIRECTORYを同梱する。
`.env` がなくてもビルド時に明示したDB_BACKENDの設定を生成し、Accessへの意図しない接続を防ぐ。
生成設定は `build/config/<backend>/.env`。設定の実値はDocs・ログへ記載しない。

## 操作と確認

セットアップ・起動・Access復帰コマンドはREADMEに集約する。
通常ビルド:

```powershell
.\.venv\Scripts\python.exe -m pip install PyInstaller Pillow
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm PinGaugeMgmt.spec
```

成果物は `dist/ピンゲージ管理.exe`。既存成果物のサイズを記録し、必要なら別ディレクトリへ退避してからビルドする。
モジュール・DLL・データはPyInstallerの `Analysis-00.toc` とexeのアーカイブ一覧で確認する。
通常版にAccess実装、pyodbc/pypyodbc、accdb/mdb、ODBCドライバー、移行資料がないこと、psycopgとGUI依存があることを確認する。
設定値の内容は出力せず、許可したキー集合だけを確認する。
実DBの確認は更新を伴わない `SELECT 1` とテーブル存在・件数確認から行う。
GUIの初期化は部署UPDATEを含むため、本番設定では無断で実行しない。

## 配布の条件

自動テスト、ビルド、収録物確認だけでは、配布先でのGUI・DB操作を保証できない。
Windows GUI確認と隔離された検証DBでの貸出・返却・確認・マスタ操作を追加する。
配布手順・復旧方法は未確定。ソースとAccess用依存を保持していることは、データの逆移行が完了したことを意味しない。
