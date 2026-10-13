---
name: datasource-build
description: Access/PostgreSQL切替とPyInstaller収録依存の分類・動作維持を検証する。
---

# DB切替・ビルド

1. docs/DATABASE.md、docs/BUILD.md、repository_factoryとspec、依存ファイルを読む。
2. 接続専用依存とGUI・業務共通依存を呼出元から分類する。Accessソースを保持する。
3. 通常はPostgreSQL、Accessは明示指定とする。設定の不一致・Accessへの暗黙フォールバックを防ぐ。
4. tests/test_backend_build.pyでAccess不在起動、URL優先順、接続失敗、両ビルド種別を確認する。
5. exeのモジュール・DLL・データを検査し、PostgreSQL・GUI依存維持とAccess依存不在を確認する。
6. サイズを比較できれば報告する。実DB検証はSELECTから始め、本番更新はdevelopment-workflowのApproval Gateに従う。
