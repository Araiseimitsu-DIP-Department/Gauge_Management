---
name: implement-feature
description: このプロジェクトの機能追加または既存機能変更を最小範囲で実装する。
---

# 機能の実装

要求・関連Docs・usecase/port/repository・JS bridge・Testsを確認し、入出力と影響範囲を整理する。
不明な業務条件はHuman Validation Requiredとして分け、独立して進められる部分を実装する。
業務判定・API入出力に関係する変更には正常・境界・異常系のTestsを用意する。
実装後はreview-codeとdevelopment-workflowのVerification Gateを適用する。
データ更新時だけ ../development-workflow/references/data-update-verification.md を参照する。
