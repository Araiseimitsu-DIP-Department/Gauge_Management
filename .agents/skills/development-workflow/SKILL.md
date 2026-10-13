---
name: development-workflow
description: 機能追加・不具合修正・改善の共通検証と承認条件を管理する。
---

# 共通開発手順

1. AGENTS.md、関連Rules、Docs、Testsを読み、Confirmed・Assumption・Unknownを分ける。
2. 新機能は implement-feature、不具合は fix-bug、DB切替・ビルドは datasource-build を使用する。
3. 実装後は review-code を適用する。AGENTS.mdの条件に該当する場合は code-simplifier を実施する。
4. 下記Verification Gateを確認し、Docsとdocs/update.mdを必要な範囲だけ更新する。
5. 結果、影響、未確認事項を日本語で報告する。

## Verification Gate

- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`。
- 起動経路の変更は `tests/test_backend_build.py` のAccess不在スモーク確認を含める。
- ビルド変更は docs/BUILD.md に沿ってexeの収録物まで確認する。
- git diff --check、git diff、git statusを確認する。
- lint・型チェックは未導入。実行不能なコマンドを必須化せずNOT RUNと理由を報告する。
- 実DB・GUI確認が未実施なら明記し、リリース準備完了とみなさない。

## Approval Gate

DB削除・初期化・リセット、大量UPDATE、本番移行、デプロイ、本番設定・認証情報変更、外部送信は、対象・件数・影響・復旧方法を具体化して明示承認を得る。
画面起動にも部署UPDATEが含まれる。本番GUI起動を読取検証として扱わない。
依頼済みの可逆なコード・Docs・Testsの変更に重複した承認を追加しない。

更新処理の変更時だけ [データ更新検証](references/data-update-verification.md) を読む。
再利用できる学びがある場合は [学びの提案・承認・反映](references/learning-feedback.md) に従う。
