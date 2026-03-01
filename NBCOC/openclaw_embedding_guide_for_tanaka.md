# たなかさん向け OpenClaw エンベディング設定ガイド

NBCOC プロキシサーバーに `/v1/embeddings` エンドポイントが追加され、OpenClaw の `memory_search` 機能で NVIDIA のエンベディングモデルを利用できるようになりました。

以下の手順で OpenClaw の `openclaw.json` を設定し、NBCOC プロキシをエンベディングプロバイダーとして利用してください。

## 1. `config.yaml` の更新

NBCOC プロキシサーバーの `config.yaml` に、`nvidia.api_key` が正しく設定されていることを確認してください。また、`default_embedding_model` が `nvidia/nv-embedqa-e5-v5` に設定されていることを確認してください。

```yaml
# config.yaml の一部
nvidia:
  api_key: "nvapi-YOUR_NVIDIA_API_KEY" # あなたのNVIDIA APIキーを設定
  default_embedding_model: "nvidia/nv-embedqa-e5-v5"
```

## 2. OpenClaw `openclaw.json` の設定

`openclaw.json` ファイルに、NBCOC プロキシをエンベディングプロバイダーとして追加します。`providers` セクションに以下の設定を追加してください。

```json
{
  "providers": [
    // 既存のプロバイダー設定...
    {
      "name": "nbcoc_embeddings",
      "type": "openai",
      "base_url": "http://localhost:8000/v1",
      "api_key": "sk-dummy", // NBCOCのconfig.yamlでproxy_api_keyを設定している場合はその値を指定
      "models": [
        {
          "id": "nvidia/nv-embedqa-e5-v5",
          "name": "NVIDIA EmbedQA E5 v5",
          "mode": "embedding"
        }
        // 必要に応じて他のNVIDIAエンベディングモデルを追加
      ]
    }
  ],
  "memory": {
    "enabled": true,
    "provider": "nbcoc_embeddings", // ここでNBCOCエンベディングプロバイダーを指定
    "model": "nvidia/nv-embedqa-e5-v5",
    "max_tokens": 8192,
    "threshold": 0.75
  }
}
```

### 設定項目の説明

*   **`name`**: プロバイダーの識別名です。`nbcoc_embeddings` のように分かりやすい名前を付けてください。
*   **`type`**: `openai` を指定します。NBCOC プロキシが OpenAI 互換の API を提供するためです。
*   **`base_url`**: NBCOC プロキシサーバーのアドレスを指定します。デフォルトでは `http://localhost:8000/v1` です。
*   **`api_key`**: NBCOC の `config.yaml` で `server.proxy_api_key` を設定している場合は、その値を指定してください。設定していない場合は、`sk-dummy` のような任意の文字列で動作します。
*   **`models`**: 利用可能なエンベディングモデルをリストします。`id` には NVIDIA のモデル名（例: `nvidia/nv-embedqa-e5-v5`）、`name` には表示名、`mode` には `embedding` を指定します。

## 3. `memory` 機能の設定

`openclaw.json` の `memory` セクションで、`provider` を上記で定義した NBCOC エンベディングプロバイダーの `name`（例: `nbcoc_embeddings`）に設定し、`model` に使用するエンベディングモデルの `id` を指定します。

これにより、OpenClaw の `memory_search` 機能が NBCOC プロキシを介して NVIDIA のエンベディングモデルを使用するようになります。

ご不明な点がありましたら、お気軽にお問い合わせください。
