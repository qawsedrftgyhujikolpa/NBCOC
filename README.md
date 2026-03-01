# NBCOC - NVIDIA Build to OpenClaw Connector

NVIDIA build.nvidia.com の無料APIを OpenAI互換プロキシとして変換し、OpenClawから利用可能にするツール。

## 機能

- `/v1/chat/completions` - チャット補完（ストリーミング対応）
- `/v1/embeddings` - テキスト埋め込み
- `/v1/models` - モデル一覧取得
- OpenClawのツール呼び出し（function calling）パラメータを自動除去
- コンテキスト長の自動トリミング

## セットアップ (WSL2 Ubuntu)

### 1. クローン & 依存ライブラリのインストール

```bash
git clone https://github.com/qawsedrftgyhujikolpa/NBCOC.git
cd NBCOC
chmod +x setup.sh
./setup.sh
```

または手動で:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. config.yaml の設定

```yaml
nvidia:
  api_key: "nvapi-YOUR-API-KEY-HERE"
  base_url: "https://integrate.api.nvidia.com/v1"
  default_model: "meta/llama-3.1-8b-instruct"
  default_embedding_model: "nvidia/nv-embedqa-e5-v5"
  default_max_context: 4096
```

APIキーは https://build.nvidia.com で無料取得できます。

### 3. 起動

NBCOCは`model.json`ファイルまたはコマンドライン引数を使用して、OpenClawのプライマリモデルを自動的に切り替えることができます。

#### モデル選択の優先順位:
1.  **コマンドライン引数**: `start-nbcoc.sh <モデル名>` の形式で指定された場合、これが最優先されます。ショートカット名（例: `kimi`, `llama`）も利用可能です。
2.  **`model.json`**: `~/NBCOC/model.json`が存在する場合、その中の`"model"`フィールドで指定されたモデルが使用されます。
3.  **デフォルト**: 上記のいずれも指定されない場合、`nbcoc/moonshotai/kimi-k2.5`がデフォルトモデルとして使用されます。

#### `model.json`の例:
`~/NBCOC/model.json`に以下の内容でファイルを作成してください。
```json
{"model": "moonshotai/kimi-k2.5"}
```

#### 使い方:
```bash
./start-nbcoc.sh          # model.jsonのモデルを使用（存在しない場合はデフォルト）
./start-nbcoc.sh kimi     # Kimi K2.5で起動
./start-nbcoc.sh llama    # Llama 3.3 70Bで起動
./start-nbcoc.sh nbcoc/qwen/qwen3-235b-a22b # フルモデルIDで起動
```

#### ショートカット名と対応モデル:
| ショートカット | フルモデルID |
|---|---|
| `kimi` | `nbcoc/moonshotai/kimi-k2.5` |
| `llama` | `nbcoc/meta/llama-3.3-70b-instruct` |
| `qwen` | `nbcoc/qwen/qwen3-235b-a22b` |
| `qwen-coder` | `nbcoc/qwen/qwen3-coder-480b-a35b-instruct` |
| `mistral` | `nbcoc/mistralai/mistral-large-3-675b-instruct-2512` |
| `deepseek` | `nbcoc/deepseek-ai/deepseek-r1-distill-qwen-32b` |
| `codestral` | `nbcoc/mistralai/codestral-22b-instruct-v0.1` |
| `nemotron` | `nbcoc/nvidia/llama-3.1-nemotron-70b-instruct` |
| `swallow` | `nbcoc/tokyotech-llm/llama-3-swallow-70b-instruct-v0.1` |


```bash
# ワンコマンド起動（プロキシ + OpenClaw再起動 + TUI自動起動）
./start-nbcoc.sh

# プロキシのみ起動
source venv/bin/activate
python3 main.py
```

デフォルトでは `http://localhost:8000` で起動します。

### 4. OpenClaw設定

`~/.openclaw/openclaw.json` の `models.providers` に以下を追加:

```json
"nbcoc": {
  "baseUrl": "http://localhost:8000/v1",
  "apiKey": "sk-dummy",
  "api": "openai-completions",
  "models": [
    {
      "id": "meta/llama-3.3-70b-instruct",
      "name": "NVIDIA Llama 3.3 70B (NBCOC)",
      "contextWindow": 131072,
      "maxTokens": 8192,
      "reasoning": false
    }
  ]
}
```

## 利用可能なモデル（厳選）

### 会話向け
| モデル | サイズ | 特徴 |
|--------|--------|------|
| meta/llama-3.3-70b-instruct | 70B | デフォルト、バランス良い |
| moonshotai/kimi-k2.5 | - | 強力な会話能力 |
| qwen/qwen3-235b-a22b | 235B | 高品質、推論対応 |
| qwen/qwen3.5-397b-a17b | 397B | 最新Qwen |
| mistralai/mistral-large-3-675b-instruct-2512 | 675B | 最大級 |
| nvidia/llama-3.1-nemotron-70b-instruct | 70B | NVIDIA独自チューニング |
| nvidia/llama-3.3-nemotron-super-49b-v1.5 | 49B | NVIDIA Super |

### コーディング向け
| モデル | サイズ | 特徴 |
|--------|--------|------|
| qwen/qwen3-coder-480b-a35b-instruct | 480B | コード特化最強クラス |
| mistralai/codestral-22b-instruct-v0.1 | 22B | Mistralコード特化 |
| mistralai/devstral-2-123b-instruct-2512 | 123B | 開発特化 |

### 推論向け
| モデル | サイズ | 特徴 |
|--------|--------|------|
| deepseek-ai/deepseek-r1-distill-qwen-32b | 32B | 推論特化 |
| qwen/qwen3-next-80b-a3b-instruct | 80B | 次世代推論 |
| qwen/qwq-32b | 32B | 推論特化 |

### 日本語向け
| モデル | サイズ | 特徴 |
|--------|--------|------|
| tokyotech-llm/llama-3-swallow-70b-instruct-v0.1 | 70B | 東工大製、日本語強い |

## 設定ファイル (config.yaml)

| 設定 | 説明 |
|------|------|
| `nvidia.api_key` | NVIDIA APIキー |
| `nvidia.base_url` | NVIDIA APIエンドポイント |
| `nvidia.default_model` | デフォルトのチャットモデル |
| `nvidia.default_embedding_model` | デフォルトのembeddingモデル |
| `nvidia.default_max_context` | デフォルトのコンテキスト上限 |
| `server.host` | プロキシのホスト |
| `server.port` | プロキシのポート |
| `server.proxy_api_key` | プロキシの認証キー（空なら認証なし） |
| `models` | モデルごとのコンテキスト上限設定 |

## 注意事項

- コンテキストのトリミングは `tiktoken` (cl100k_base) を使用した概算に基づいています
- `max_tokens` がリクエストに含まれない場合、デフォルトで `1024` が設定されます
- 405Bモデルは一部アカウントで利用不可の場合があります
- OpenClawのfunction calling パラメータは自動的に除去されます

## ライセンス

MIT
