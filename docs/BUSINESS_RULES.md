# コードで確認した業務条件

本書は現在の実装から確認した条件のみを記載する。変更の許可や新仕様の提案ではない。

| 領域 | 条件と根拠 | 自動テスト |
|---|---|---|
| 貸出 | 日付・機番・担当者・少なくとも1つのサイズが必要。サイズは空欄除去・大文字化。`utils/validators.py`、`lending_usecase.py` | `test_business_rules.py` |
| 返却 | 個別返却は対象ID・日付が必要。ケースNoは空白除去・大文字化、必須かつ2文字以内。`operation_usecase.py` | `test_business_rules.py` |
| 確認 | ケースNoは必須かつ20文字以内。個別確認は対象ID、一括確認は空でないID一覧が必要。`operation_usecase.py` | 境界値は `test_business_rules.py`、DB連携未検証 |
| PGマスタ | サイズ・保有数・ケースNoが必須。貸出履歴に参照されるサイズは削除禁止。`master_usecase.py` | 削除禁止は `test_business_rules.py` |
| 担当者 | 更新時は担当者IDと氏名が必須。`master_usecase.py` | 未追加 |

UI操作仕様はREADMEの画面運用メモと `DESIGN/DESIGN.md` を参照。
部署補正は画面の `WebviewBridge.bootstrap()` から `normalize_staff_departments()` が呼ばれ、DBのUPDATEを実行する。
本番DB設定での画面起動は単なる読取検証ではない。

在庫超過・同一サイズの重複貸出に関する運用上の許否、確認完了の業務上の解釈は、人間確認が必要。
コードにない制約を推測で追加しない。
