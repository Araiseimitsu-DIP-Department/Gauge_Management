# Access -> PostgreSQL 移行手順書

## 目的

Access データベース `ピンゲージ管理DB.accdb` を PostgreSQL `pingauge_management_db` へ移行し、アプリを PostgreSQL バックエンドで運用するための手順書です。

Access 側の元テーブル・元カラムは日本語名のまま読み取り、移行スクリプトで PostgreSQL の英語物理名へマッピングします。Access のクエリ相当の処理は PostgreSQL のビューでは作成せず、アプリの Python repository 層で JOIN / 条件処理します。

## 移行先

```text
host     : 192.168.1.120
database : pingauge_management_db
schema   : public
encoding : UTF8
timezone : Asia/Tokyo
```

`.env` は次の形式です。

```env
DB_BACKEND=postgres
POSTGRES_CONNECTION_URL=postgresql://postgres:password@192.168.1.120:5432/pingauge_management_db
DATABASE_URL=postgresql://postgres:password@192.168.1.120:5432/pingauge_management_db
POSTGRES_SCHEMA=public
```

`POSTGRES_CONNECTION_URL` を優先します。`DATABASE_URL` は `docs/pingauge_management_db` の移行ツール互換用で、アプリ側でもフォールバックとして読み込みます。

## 移行元

```text
\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb
```

Access ファイルを読むには、共有フォルダへの読み取り権限が必要です。Access のロックファイル作成が絡む場合があるため、状況によってはフォルダへの書き込み権限も必要です。

## 物理名マッピング

| Access テーブル | PostgreSQL テーブル |
|---|---|
| `t_PGマスタ` | `pin_gauge_master` |
| `t_担当者マスタ` | `staff_master` |
| `t_貸出` | `pin_gauge_lending` |

| Access カラム | PostgreSQL カラム | 対象 |
|---|---|---|
| `サイズ` | `size` | `pin_gauge_master`, `pin_gauge_lending` |
| `保有数` | `owned_quantity` | `pin_gauge_master` |
| `ケースNo` | `case_no` | `pin_gauge_master` |
| `担当者ID` | `staff_id` | `staff_master`, `pin_gauge_lending` |
| `担当者名` | `staff_name` | `staff_master` |
| `部署` | `department` | `staff_master` |
| `かな` | `kana` | `staff_master` |
| `表示` | `display_flag` | `staff_master` |
| `ID` | `id` | `pin_gauge_lending` |
| `機番` | `machine_no` | `pin_gauge_lending` |
| `貸出日` | `lent_date` | `pin_gauge_lending` |
| `返却日` | `returned_date` | `pin_gauge_lending` |
| `完了フラグ` | `completion_flag` | `pin_gauge_lending` |

## PostgreSQL テーブル

### `pin_gauge_master`

| カラム | 型 | 内容 |
|---|---|---|
| `size` | `varchar(20)` | サイズまたは特殊ゲージ名 |
| `owned_quantity` | `integer` | 保有数 |
| `case_no` | `varchar(5)` | ケースNo |

### `staff_master`

| カラム | 型 | 内容 |
|---|---|---|
| `staff_id` | `varchar(2)` | 担当者ID |
| `staff_name` | `varchar(5)` | 担当者名 |
| `department` | `varchar(2)` | 部署 |
| `kana` | `varchar(1)` | 並び替え用かな |
| `display_flag` | `varchar(1)` | `Y` / `N` |

### `pin_gauge_lending`

| カラム | 型 | 内容 |
|---|---|---|
| `id` | `bigint identity` | 貸出ID |
| `size` | `varchar(20)` | サイズまたは特殊ゲージ名 |
| `staff_id` | `varchar(2)` | 担当者ID |
| `machine_no` | `varchar(4)` | 機番。返却後は `返-7` など |
| `lent_date` | `timestamp` | 貸出日 |
| `returned_date` | `timestamp` | 返却日 |
| `completion_flag` | `varchar(1)` | `NULL` / `N` / `Y` |

## SQL ファイル

| ファイル | 役割 |
|---|---|
| `database/postgresql/001_schema.sql` | 英語物理名のテーブル作成 |
| `database/postgresql/002_indexes.sql` | 検索用インデックス |
| `database/postgresql/003_constraints.sql` | PK / CHECK / FK 制約 |
| `database/postgresql/004_rename_to_english.sql` | 既存の日本語物理名テーブルを現行英語名へ変更する一回限りのSQL |
| `database/postgresql/005_reconcile_loan_sizes.sql` | `pin_gauge_lending.size` と `pin_gauge_master.size` の参照欠損補正 |
| `database/postgresql/010_import_from_csv.sql` | CSVインポート用テンプレート |
| `database/postgresql/020_validation.sql` | 件数・NULL・重複・参照欠損検証 |
| `database/postgresql/migration_notes.md` | 実行結果メモ |

## サイズ補正方針

Access の貸出履歴には、`1.03` のような小数桁違いのサイズと、`BM10-12` や `M4*P0.7` のような特殊ゲージ名が含まれることがあります。

移行時は次の方針で整合性を取ります。

1. `1.03` -> `1.030` のように、既存 `pin_gauge_master.size` に一致する数値サイズは3桁表記へ補正する。
2. それでも `pin_gauge_master` に存在しない履歴上のサイズ・特殊ゲージ名は、履歴を消さずに `pin_gauge_master` へ追加する。
3. 追加時は `owned_quantity = 0`, `case_no = NULL` とする。
4. 補正後に `pin_gauge_lending.size -> pin_gauge_master.size` の FK を適用する。

この処理は `scripts/migrate_access_to_postgres.py` に組み込み済みです。SQL単体で補正したい場合は `005_reconcile_loan_sizes.sql` を使用します。

## 本番移行手順

### 1. 事前停止

Access アプリ利用者へ停止時間を連絡し、移行中は Access 側を更新しない状態にします。

### 2. バックアップ

Access ファイルと PostgreSQL の既存DBをバックアップします。

### 3. dry-run

PostgreSQL へ書き込まず、Access から読み取れるか確認します。

```powershell
.\.venv\Scripts\python.exe scripts\migrate_access_to_postgres.py --dry-run
```

期待例:

```text
pin_gauge_master: 2030 rows
staff_master: 29 rows
pin_gauge_lending: 32229 rows
Dry run complete. PostgreSQL was not modified.
```

### 4. 本投入

`--apply-schema --truncate` でテーブルを初期化して再投入します。

```powershell
.\.venv\Scripts\python.exe scripts\migrate_access_to_postgres.py --apply-schema --truncate
```

このスクリプトは次を行います。

- Access 3テーブルを読み取り
- PostgreSQL 英語物理名へ変換して投入
- 数値サイズの3桁補正
- 不足する履歴サイズを `pin_gauge_master` にプレースホルダ追加
- `pin_gauge_lending.id` の identity sequence 調整

`docs/pingauge_management_db/migrate_access_to_postgres_pingauge_management_db.py` は、同フォルダのメタ情報を使う対象専用スクリプトです。既存テーブルがある場合は停止する設計なので、再投入ではなく新規移行・件数検証用として扱います。

### 5. インデックス作成

```text
database/postgresql/002_indexes.sql
```

### 6. 制約適用

```text
database/postgresql/003_constraints.sql
```

`003_constraints.sql` は、`020_validation.sql` で参照欠損が 0 であることを確認してから実行します。

### 7. 検証

```text
database/postgresql/020_validation.sql
```

確認項目:

- `pin_gauge_master`, `staff_master`, `pin_gauge_lending` の件数
- `case_no`, `returned_date`, `completion_flag` の NULL 件数
- `size`, `staff_id`, `id` の重複
- `pin_gauge_lending.size -> pin_gauge_master.size` の欠損
- `pin_gauge_lending.staff_id -> staff_master.staff_id` の欠損
- アプリ用の未完了・返却対象・確認待ち件数

2026-06-15 確認済み例:

```text
pin_gauge_master: 2030
staff_master: 29
pin_gauge_lending: 32229
```

### 8. アプリ確認

`.env` を `DB_BACKEND=postgres` にして `main.py` を起動します。

```powershell
.\.venv\Scripts\python.exe main.py
```

確認する操作:

- アプリ起動
- 貸出一覧検索
- 担当者一覧
- PGマスタ一覧
- 返却対象一覧
- 確認待ち一覧
- 返却後、確認画面の「確認済みバッチ」が再読込ボタンなしで更新されること

更新操作は、本番切替判断後に行います。

## アプリ側の実装

PostgreSQL 側は次の実装が英語物理名を参照します。

```text
app/infrastructure/postgres/repositories/
app/infrastructure/postgres/mappers/
```

Access 側の repository は日本語物理名の Access DB を扱うため、そのままです。

## 切り戻し

問題があれば `.env` を Access に戻します。

```env
DB_BACKEND=access
ACCESS_DB_DIRECTORY=\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb
```

切り戻し後、PostgreSQL 側のデータまたは repository 実装を修正して再移行します。

## 本番移行を依頼するときの指示例

```text
PostgreSQL本番移行を実行してください。
手順は docs/postgresql-migration.md と database/postgresql/migration_notes.md に従ってください。
実行前に dry-run を行い、件数を確認してから --apply-schema --truncate で本投入してください。
投入後、002_indexes.sql、003_constraints.sql、020_validation.sql を実行し、結果を migration_notes.md に記録してください。
```
