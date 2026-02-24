# NVIDIA API to OpenAI Proxy

このプロジェクトは、NVIDIA API (`build.nvidia.com`) を OpenAI 互換の API エンドポイントに変換する中間プロキシサーバーです。
OpenClaw などの OpenAI 互換クライアントで NVIDIA のモデル（Llama 3.1 等）を簡単に利用できるように設計されています。

## 主な機能

- **OpenAI 互換エンドポイント**: `/v1/chat/completions` および `/v1/models` を提供。
- **コンテキスト管理**: 設定された最大コンテキスト長を超えないよう、古いメッセージを自動的にトリミングします。
- **ストリーミング対応**: `stream: true` によるリアルタイムレスポンスをサポート。
- **柔軟な設定**: `config.yaml` で API キー、デフォルトモデル、モデルごとのコンテキスト長などを設定可能。
- **WSL2 最適化**: Ubuntu 環境で簡単にセットアップ・実行可能。

## セットアップ手順 (WSL2 Ubuntu)

1. **ディレクトリへ移動**
   ```bash
   cd /home/ubuntu/nvidia-proxy/
   ```

2. **セットアップスクリプトの実行**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **設定の編集**
   `config.yaml` を開き、`nvidia.api_key` にあなたの NVIDIA API キーを入力してください。
   ```yaml
   nvidia:
     api_key: "nvapi-..."  # ここにキーを入力
   ```

## 起動方法

仮想環境を有効化して、サーバーを起動します。

```bash
source venv/bin/activate
python3 main.py
```

デフォルトでは `http://localhost:8000` で起動します。

## クライアント（OpenClaw 等）での設定例

OpenClaw などのクライアントで以下のように設定してください。

- **API Base URL**: `http://localhost:8000/v1`
- **API Key**: `config.yaml` の `server.proxy_api_key` が空の場合は適当な文字列（例: `sk-dummy`）で動作します。
- **Model**: `meta/llama-3.1-405b-instruct` など、NVIDIA で利用可能なモデル名。

## 設定ファイル (config.yaml) について

- `nvidia.default_max_context`: モデルごとの設定がない場合に使用されるデフォルトのコンテキスト制限。
- `models`: モデルごとの特定のコンテキスト制限（例: Llama 3.1 は 128k など）を記述します。
- `server.proxy_api_key`: プロキシ自体に認証をかけたい場合に設定します。

## 注意事項

- コンテキストのトリミングは `tiktoken` (cl100k_base) を使用した概算に基づいています。
- `max_tokens` がリクエストに含まれない場合、NVIDIA API の仕様に合わせてデフォルトで `1024` が設定されます。
