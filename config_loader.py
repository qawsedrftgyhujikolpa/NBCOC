import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class NvidiaConfig:
    api_key: str = ""
    base_url: str = "https://integrate.api.nvidia.com/v1"
    default_model: str = "meta/llama-3.1-405b-instruct"
    default_max_context: int = 4096
    default_embedding_model: str = "nvidia/nv-embedqa-e5-v5"

@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    proxy_api_key: str = ""

@dataclass
class ModelConfig:
    max_context: int = 4096

@dataclass
class AppConfig:
    nvidia: NvidiaConfig = field(default_factory=NvidiaConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    models: Dict[str, ModelConfig] = field(default_factory=dict)

def load_config(path: str = "config.yaml") -> AppConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}

    nvidia_raw = raw.get("nvidia", {})
    nvidia = NvidiaConfig(
        api_key=nvidia_raw.get("api_key", ""),
        base_url=nvidia_raw.get("base_url", "https://integrate.api.nvidia.com/v1"),
        default_model=nvidia_raw.get("default_model", "meta/llama-3.1-405b-instruct"),
        default_max_context=nvidia_raw.get("default_max_context", 4096),
        default_embedding_model=nvidia_raw.get("default_embedding_model", "nvidia/nv-embedqa-e5-v5"),
    )

    server_raw = raw.get("server", {})
    server = ServerConfig(
        host=server_raw.get("host", "0.0.0.0"),
        port=server_raw.get("port", 8000),
        proxy_api_key=server_raw.get("proxy_api_key", ""),
    )

    models = {}
    for model_name, model_data in raw.get("models", {}).items():
        models[model_name] = ModelConfig(
            max_context=model_data.get("max_context", nvidia.default_max_context)
        )

    return AppConfig(nvidia=nvidia, server=server, models=models)

config = load_config()
