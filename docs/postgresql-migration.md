# Access -> PostgreSQL 移行メモ

## 目的

本書は、現行の `ピンゲージ管理` アプリと、`docs/ピンゲージ管理_meta.md` に含まれる Access スキーマ情報をもとに、将来 Microsoft Access から PostgreSQL へ本格移行する際の設計メモをまとめたものです。

現行アプリは、貸出・返却・確認・PGマスタ・担当者マスタを扱う業務アプリです。GUI は `pywebview`、業務ロジックは `application / services / infrastructure` に分離されています。

このメモでは、初回移行で業務を止めずに動かすことを優先し、Access の物理名をできるだけ維持する方針で整理します。未確認の点は未確認と明記し、推測だけで確定扱いしません。

## 現行アプリの構成

```text
Gauge_Management/
  main.py                         起動入口
  app/
    bootstrap.py                  pywebview ウィンドウ生成と起動
    config/                       .env 読み込みと DB 設定
    application/                  usecase と repository port
    domain/                       ドメインモデル
    infrastructure/               Access / PostgreSQL 実装
    repositories/                 接続補助
    services/                     GUI 向けサービス層
    shared/                       共通 Result / Error
    utils/                        環境変数読込、バリデーション
    webview/                      HTML / CSS / JavaScript の GUI
  docs/
    精密計測具のアイコン.png    元アイコン
    pingauge.ico                  PyInstaller 用アイコン
    SETUP.md                      初期設定メモ
    DESIGN.md                     画面設計メモ
    ピンゲージ管理_meta.md        Access スキーマの元資料
```

### 現行の DB 切替

- `DB_BACKEND=access`
  - Access `.accdb` を利用
- `DB_BACKEND=postgres`
  - PostgreSQL を利用

設定キーは以下です。

```env
APP_ENV=local
APP_NAME=ピンゲージ管理
DB_BACKEND=access
ACCESS_DB_DIRECTORY=C:\Path\To\AccessFolder

# PostgreSQL
POSTGRES_CONNECTION_URL=postgresql://user:password@localhost:5432/pingauge_management
POSTGRES_SCHEMA=public
```

## 現状サマリ

### 実装済み機能

- 貸出登録
- 貸出一覧の検索、編集、削除
- 返却処理
- 返却済みデータの確認処理
- PGマスタの検索、編集、削除
- 担当者マスタの検索、編集

### 現在の DB 依存ポイント

- `app/infrastructure/access/repositories/*.py` が Access SQL を直接実行している
- `app/infrastructure/postgres/repositories/*.py` が PostgreSQL SQL を実行している
- `app/webview/backend.py` が画面と usecase の橋渡しをしている
- `app/webview/frontend.py` が画面の状態管理と描画を担う
- `app/services/*.py` が GUI 向けの入出力整形を行う

## Access スキーマの要約

`docs/ピンゲージ管理_meta.md` では、Access 側で次の 3 テーブルが確認できます。

| テーブル | 行数 | 備考 |
|---|---:|---|
| `t_PGマスタ` | 2,024 | PG サイズ、数量、ケースNo |
| `t_担当者マスタ` | 29 | 担当者情報 |
| `t_貸出` | 30,930 | 貸出履歴 |

### 補足

- 参照整合性の定義は ODBC 側では取得できていない
- Access の export では 3 テーブルとも `SYNONYM` として見えている
- 初回移行では、外部キーを SQL で明示しつつ、元の物理名を維持する方針が安全

## 移行方針

### 方針 1: 初回移行では物理名を維持する

現行コードは、Access の日本語識別子を前提にしています。初回移行では次を推奨します。

- テーブル名は Access と同じ名前を維持する
- カラム名も Access と同じ名前を維持する
- PostgreSQL でも UTF-8 の日本語識別子を使う
- SQL は必ずダブルクォートで囲う

この方針にすると、アプリ改修は主に接続設定と SQL 方言差分に限定できます。

### 方針 2: Access 固有構文を排除する

移行時に置換が必要になる代表例です。

- `IIf(...)` は PostgreSQL の `CASE` に置換する
- `SELECT @@IDENTITY` は `INSERT ... RETURNING` に置換する
- `DELETE * FROM ...` は `DELETE FROM ...` に置換する
- 空文字と `NULL` の扱いは明文化する

### 方針 3: 一時テーブルは作りすぎない

現行アプリは、画面表示や帳票相当のデータをメモリ上で組み立てられる構造です。Access 互換のためだけに一時テーブルを増やすより、初回は常設テーブルを最小限に絞る方が保守しやすいです。

## 現行ロジックの要点

### PGマスタ

- サイズで検索、編集、削除する
- `サイズ`, `数量`, `ケースNo` を扱う
- サイズ検索は `0.120` と `0.12` の揺れを吸収する

### 担当者マスタ

- 担当者ID、氏名、部署、かな、表示フラグを扱う
- 表示フラグは `Y / N` で扱う
- 部署の正規化は起動時に 1 回だけまとめて行う

### 貸出

- 1 回の登録で 20 件のサイズをまとめて登録する
- 貸出一覧はサイズ検索と機番検索を切り替える
- 機番は画面側で `機番` として入力し、前置きと番号を組み合わせる
- 返却時は返却日を入れ、機番を `返...` 系の表記へ更新する
- 確認処理では返却済みデータを確認済みに更新する

## PostgreSQL 推奨設計

### DB 基本設定

```text
db_name      : pingauge_management
encoding     : UTF8
lc_collate   : ja_JP.UTF-8
lc_ctype     : ja_JP.UTF-8
timezone     : Asia/Tokyo
default_schema: public
```

### 推奨テーブル

初回移行で最低限必要なのは次の 3 テーブルです。

- `t_PGマスタ`
- `t_担当者マスタ`
- `t_貸出`

参照整合性を厳密にするなら、外部キーは PostgreSQL で明示することを推奨します。

## テーブル設計

### 1. `t_PGマスタ`

PG サイズごとの数量とケースNo を持つマスタです。

| カラム | 推奨型 | 必須 | 備考 |
|---|---|---|---|
| `サイズ` | `varchar(20)` | Yes | 主キー候補 |
| `数量` | `integer` | Yes | 現行コードでは数値として扱う |
| `ケースNo` | `varchar(5)` | No | 空文字でも可 |

推奨制約:

- `PRIMARY KEY ("サイズ")`
- `CHECK ("数量" >= 0)`

推奨インデックス:

- `("サイズ")`

### 2. `t_担当者マスタ`

担当者の一覧です。貸出、返却、確認で参照します。

| カラム | 推奨型 | 必須 | 備考 |
|---|---|---|---|
| `担当者ID` | `varchar(2)` | Yes | 主キー候補 |
| `氏名` | `varchar(50)` | Yes | 画面表示名 |
| `部署` | `varchar(10)` | No | 例: `製造`, `数値`, `その他` |
| `かな` | `varchar(50)` | No | 検索、並び替え用 |
| `表示` | `char(1)` | Yes | `Y / N` |

推奨制約:

- `PRIMARY KEY ("担当者ID")`
- `CHECK ("表示" IN ('Y', 'N'))`

推奨インデックス:

- `("氏名")`
- `("部署")`
- `("かな")`
- `("表示")`

### 3. `t_貸出`

貸出履歴の中心テーブルです。現行アプリのメインテーブルです。

| カラム | 推奨型 | 必須 | 備考 |
|---|---|---|---|
| `ID` | `bigserial` | Yes | 主キー |
| `サイズ` | `varchar(20)` | Yes | PG サイズ |
| `担当者ID` | `varchar(2)` | Yes | `t_担当者マスタ` 参照 |
| `機番` | `varchar(20)` | Yes | 機番の複合文字列 |
| `貸出日` | `date` | Yes | 貸出日 |
| `返却日` | `date` | No | 返却前は NULL |
| `確認フラグ` | `char(1)` | No | `Y / N / NULL` を想定 |

推奨制約:

- `PRIMARY KEY ("ID")`
- `FOREIGN KEY ("担当者ID") REFERENCES "t_担当者マスタ" ("担当者ID")`
- `CHECK ("確認フラグ" IS NULL OR "確認フラグ" IN ('Y', 'N'))`

推奨インデックス:

- `("サイズ")`
- `("担当者ID")`
- `("機番")`
- `("貸出日")`
- `("返却日")`
- `("確認フラグ")`

### `確認フラグ` の運用メモ

現行ロジックから読む限り、`確認フラグ` は次のように使われています。

- `NULL`: 未返却
- `N`: 返却済み、未確認
- `Y`: 確認済み

この解釈は実装に基づく推定です。最終確定前に Access 実データで再確認してください。

## 現行処理との対応

### 貸出登録

- 画面から日付、機番、担当者、サイズ群を受け取る
- 20 件のサイズを個別に INSERT する
- 1 登録あたり複数行になる

### 貸出一覧の検索

- サイズで検索
- 機番で検索
- 前方一致モードを持つ

### 貸出編集

- 既存の 1 行だけを更新する
- サイズ、機番、担当者、貸出日を更新対象にする

### 返却

- 対象機番の未返却データを取得する
- 返却日を設定する
- 機番は返却済み表記へ更新する

### 確認

- 返却済みで未確認のデータを対象にする
- 個別確認と一括確認がある
- 確認後は確認フラグを `Y` にする

## PostgreSQL での SQL 実装メモ

### INSERT 後の ID 取得

```sql
INSERT INTO "t_貸出" (
  "サイズ", "担当者ID", "機番", "貸出日"
)
VALUES (
  :size, :staff_id, :machine_code, :lent_on
)
RETURNING "ID";
```

### 部署の一括正規化

Access では `IIf` を使うより、PostgreSQL では `CASE` に寄せます。

```sql
UPDATE "t_担当者マスタ"
SET "部署" = CASE "部署"
  WHEN '旧値1' THEN '新値1'
  WHEN '旧値2' THEN '新値2'
  ELSE "部署"
END
WHERE "部署" IN ('旧値1', '旧値2');
```

### 更新単位

以下は 1 トランザクションでまとめることを推奨します。

- 貸出登録
- 貸出編集
- 返却
- 確認
- マスタ保存、削除

## 移行時の注意点

### 1. 空文字と NULL を整理する

Access では空文字と NULL が混在しやすいです。移行前に次の項目を確認してください。

- `ケースNo`
- `かな`
- `部署`
- `機番`
- `返却日`

### 2. 機番の表記ルールを固定する

現行 UI では機番を前置き + 番号で扱っています。PostgreSQL 側でも文字列結合の結果をそのまま保存するか、正規化して別カラムに分けるかを先に決めてください。

初回移行では、現行の 1 カラム構成をそのまま維持する方が安全です。

### 3. 参照整合性の追加は段階的に行う

最初から厳しい制約を入れると、既存データの不整合で移行が止まりやすくなります。まずはデータ移行を優先し、後から制約を強くする進め方が現実的です。

### 4. 文字列比較は明示的に行う

Access 由来の曖昧な比較は避け、PostgreSQL では型をそろえて比較してください。

## 初回移行で最低限必要なもの

- `t_PGマスタ`
- `t_担当者マスタ`
- `t_貸出`
- `DB_BACKEND=postgres` の設定
- `POSTGRES_CONNECTION_URL`
- 必要に応じた `POSTGRES_SCHEMA`

## 次にやること

1. Access 実ファイルから実カラム名と NULL 分布を再確認する
2. PostgreSQL 用 DDL を別ファイルとして確定する
3. 必要なら `t_貸出` の正規化方針を確定する
4. 既存 Access データを PostgreSQL へ移行するスクリプトを作る
5. 切替後の動作確認を行う

## 補足

- 本書は現行の `ピンゲージ管理` 実装に合わせた暫定メモです
- 未確認項目は、実データの調査後に確定してください
- 現行アプリはすでに `Access / PostgreSQL` の両方を扱える構造になっています
