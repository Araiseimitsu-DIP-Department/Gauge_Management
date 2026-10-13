# 自動テスト

標準ライブラリunittestを使用します。実DBに接続せず、Windows GUIを表示しません。

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

- `test_backend_build.py`: Accessインポートを禁止したPostgreSQL起動経路、DB選択、URL優先順、接続失敗、設定分離、ビルド種別不一致の拒否。
- `test_business_rules.py`: サイズ正規化、貸出必須サイズ、返却・確認ケースNoの境界、対象未選択時の更新禁止、参照中マスタの削除禁止。
- `test_postgres_sequence.py`: 採番同期、後戻り防止、旧不足行追記の同期順とrollback、接続エラーとSQLエラーの区別。

任意依存pyodbcが未導入の場合はAccess選択テスト1件のみskipします。
GUI起動はcreate_window/startを模擬します。実画面表示と実DB更新の確認は別途必要です。
業務仕様とテスト対応は `docs/BUSINESS_RULES.md`、収録物確認は `docs/BUILD.md` を参照してください。
