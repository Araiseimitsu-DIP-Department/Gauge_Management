---
name: review-code
description: 実装・修正後に既存仕様、回帰、入出力、DB影響と未検証事項をレビューする。
---

# コードレビュー

差分と関連Docs・Testsを比較し、要求との整合、分岐、None/空文字、境界値、日付、型、DBの更新対象、エラー処理、不要変更を確認する。
指摘はCritical/High/Medium/Lowで分類し、Critical/Highが残れば配布可能と判断しない。
DB切替ではAccess専用と共通依存を混同せず、未設定・接続失敗時の経路も確認する。
development-workflowのVerification Gateを使用する。
更新関連だけ ../development-workflow/references/data-update-verification.md を読む。
学びがあれば ../development-workflow/references/learning-feedback.md に従う。
