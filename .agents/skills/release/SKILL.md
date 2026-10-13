---
name: release
description: Windows onefile成果物の収録物と配布前の検証状況を確認する。
---

# 配布前確認

docs/BUILD.mdとREADMEを読み、テスト、設定例、Docs、履歴、ビルド種別を確認する。
datasource-buildで収録物を調べ、GUI・実DB未確認は区別して報告する。
git diff/statusとdevelopment-workflowの両Gateを確認する。ビルド成功だけで配布完了としない。
本番への配布は対象と成果物を具体化して承認後に行う。
更新機能を含むリリースは ../development-workflow/references/data-update-verification.md を参照する。
