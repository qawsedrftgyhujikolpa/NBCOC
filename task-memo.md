# NBCOC アップデートタスク

## やること
1. NBCOCに /v1/embeddings エンドポイントを追加する
   - NVIDIAのembeddingモデル（nvidia/nv-embedqa-e5-v5 等）に対応
   - OpenClawのmemory_search機能が使えるようにする
2. 更新したコードをGitHubにプッシュする
3. config.yamlにembedding設定を追加する

## 認証情報
(GitHub PATはセキュリティ上の理由から削除されました)

- リポジトリ: https://github.com/qawsedrftgyhujikolpa/NBCOC

## 現在のNVIDIA APIキー（たなかさん側）
- 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

## 使えるembeddingモデル（NVIDIAモデル一覧より）
- nvidia/nv-embedqa-e5-v5
- nvidia/nv-embedqa-mistral-7b-v2
- nvidia/nv-embed-v1
- baai/bge-m3
- snowflake/arctic-embed-l

## OpenClaw設定メモ
- openclaw.jsonのnbcocプロバイダーにembeddingモデルも追加が必要
- memory機能でembeddingプロバイダーとしてnbcocを指定する設定も案内する
