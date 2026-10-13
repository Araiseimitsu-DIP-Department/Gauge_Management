# AIハーネス調査・設計

## Confirmed

- 既存のPython/pywebview業務アプリ。起動・構成はARCHITECTURE、業務条件はBUSINESS_RULES、DBはDATABASEに集約する。
- ビルドはPyInstaller onefile。PostgreSQLとAccessのrepository切替があり、フォールバックはない。
- 調査開始時のTestsはREADMEと空のパッケージのみ。lint・型チェックの設定は確認できなかった。
- READMEはpywebviewを記載していたが、SETUPは旧 `app/ui`・PySide6を記載していた。現行コードに合わせSETUPをREADMEへの参照に整理する。
- アプリはOS環境変数ではなく設定ファイルを読み込む。ソース実行とfrozen実行で探索場所が異なる。
- 移行スクリプト、DDL、マスタのDELETE・部署UPDATEは本番データへ影響し得る。

## Assumption

- 配布先は同様のWindows環境と想定するが、.NET・WebView2のインストール状態は未確認。
- 過去の移行結果は現在のDB件数と一致するとは限らない。

## Unknown

- 本番リリース経路、承認者、バックアップ・復旧の実運用。
- 実DBを更新する主要機能の今回の統合検証、配布先GUI確認。
- 機番・サイズの業務上の例外、在庫超過や重複の運用。未確認事項を仕様として追加しない。

## 役割分担と生成設計

| 対象 | 役割 |
|---|---|
| AGENTS.md | 既存ルールを保持し、Docs・Skillsへの参照を追加 |
| .cursor/rules | 恒常的制約。既存AGENTSの品質規約は再記載せず参照 |
| .agents/skills/development-workflow | 共通のVerification/Approval Gate・作業振り分け |
| implement-feature / fix-bug | 要求または再現条件に応じた調査・実装手順 |
| review-code / code-simplifier | 回帰・エラー確認と仕様を保つ簡素化。レビューと実装整理を区別 |
| release | onefile収録物・配布前の確認 |
| datasource-build | 独立して繰り返すDB切替と依存の分類・収録物確認 |
| docs | 現行構成・仕様・未確定事項。既存移行資料を再生成しない |
| tests | DB切替・起動分離と業務条件の自動検証 |
| docs/update.md | 重要な変更履歴のみ |

Domain SkillはDB切替・ビルドに限定する。業務ロジックはまずDocsとtestsで明確化し、重複するSkillを増やさない。
外部HTTP APIのDocsは生成しない。JS bridgeの契約は関連コードと変更時のTestsで確認する。
lint・型チェックは未導入でNOT RUNと報告し、存在しない必須コマンドを作らない。
