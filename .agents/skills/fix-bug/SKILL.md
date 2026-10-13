---
name: fix-bug
description: 報告された不具合の再現、原因特定、最小修正と回帰検証を行う。
---

# 不具合の修正

現象・発生条件・期待動作を整理し、再現、コード・ログ・Docs確認、原因特定、最小修正、再現・回帰テストの順に進める。
原因候補をConfirmedとしない。エラー原因はログから確認し、設定実値を露出させない。
review-codeとdevelopment-workflowのVerification Gateを適用する。
更新関連だけ ../development-workflow/references/data-update-verification.md を読む。
再利用できる学びは ../development-workflow/references/learning-feedback.md に従って提案する。
