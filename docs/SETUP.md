# セットアップ

セットアップ・起動・必要な設定キー・Access復帰手順は [README](../README.md) に集約しています。
現在のGUIはpywebviewです。構成は [ARCHITECTURE.md](ARCHITECTURE.md)、ビルドと検証は [BUILD.md](BUILD.md) を参照してください。

Accessの保存先はフォルダまたはファイルパスで指定できますが、接続ファイル名は既存実装どおり `ピンゲージ管理DB.accdb` に固定です。
本番DBを設定した画面の初期化は部署補正UPDATEを含みます。読取だけの疎通確認にはGUIを起動しないでください。
