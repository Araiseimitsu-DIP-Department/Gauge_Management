# 自動テスト

標準ライブラリunittestを使用します。実DBに接続せず、Windows GUIを表示しません。

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

- `test_backend_build.py`: Accessインポートを禁止したPostgreSQL起動経路、DB選択、URL優先順、接続失敗、設定分離、ビルド種別不一致の拒否。
- `test_business_rules.py`: サイズ正規化、貸出必須サイズ、返却・確認ケースNoの境界、対象未選択時の更新禁止、参照中マスタの削除禁止。
- `test_postgres_sequence.py`: 採番同期、後戻り防止、旧不足行追記の同期順とrollback、接続エラーとSQLエラーの区別。
- `test_frontend_dates.py`: Node.jsで日付同期の実装を実行し、日付変更、同日内の手動指定保持、画面復帰、年・月またぎ、入力保持を検証。Node.jsがない環境ではskip。
- `test_operation_table.py`: Node.jsで二列表示の全行保持、順序、元の行番号、左右両列の選択ID、HTMLエスケープを検証。Node.jsがない環境ではskip。
- `test_ui_preferences.py`: 表示モードの保存・再読込、不正設定のフォールバック、保存失敗時の旧設定保持、bridge応答、HTMLへのテーマ・バージョン埋込みを検証。
- `test_return_case_input.py`: Node.jsで返却ケースNoの数字限定判定と、英字・記号・全角数字入力時の返却ボタン無効化を検証。

任意依存pyodbcが未導入の場合はAccess選択テスト1件のみskipします。
GUI起動はcreate_window/startを模擬します。実画面表示と実DB更新の確認は別途必要です。
業務仕様とテスト対応は `docs/BUSINESS_RULES.md`、収録物確認は `docs/BUILD.md` を参照してください。
