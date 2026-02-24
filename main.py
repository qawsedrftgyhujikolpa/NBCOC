import json
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import uvicorn

from config_loader import config
from utils import trim_messages

app = FastAPI(title="NVIDIA API to OpenAI Proxy")
security = HTTPBearer()

# Shared HTTP client for non-streaming
client = httpx.AsyncClient(base_url=config.nvidia.base_url, timeout=60.0)

async def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    if config.server.proxy_api_key and auth.credentials != config.server.proxy_api_key:
        raise HTTPException(status_code=401, detail="Invalid Proxy API Key")
    return auth.credentials

@app.get("/v1/models")
async def list_models(token: str = Depends(verify_token)):
    headers = {
        "Authorization": f"Bearer {config.nvidia.api_key}",
        "Accept": "application/json"
    }
    try:
        response = await client.get("/models", headers=headers)
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, token: str = Depends(verify_token)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    model = body.get("model", config.nvidia.default_model)
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    
    # Get max context
    max_context = config.nvidia.default_max_context
    if model in config.models:
        max_context = config.models[model].max_context
    
    # Context trimming logic
    reserved_for_response = body.get("max_tokens", 1024)
    safe_limit = max_context - reserved_for_response
    
    trimmed_messages = trim_messages(messages, safe_limit, model)
    
    nvidia_payload = body.copy()
    nvidia_payload["messages"] = trimmed_messages
    
    # Ensure max_tokens is present as some NVIDIA models require it
    if "max_tokens" not in nvidia_payload:
        nvidia_payload["max_tokens"] = 1024

    headers = {
        "Authorization": f"Bearer {config.nvidia.api_key}",
        "Content-Type": "application/json",
    }

    if stream:
        return StreamingResponse(
            stream_nvidia_response(nvidia_payload, headers),
            media_type="text/event-stream"
        )
    else:
        try:
            response = await client.post("/chat/completions", json=nvidia_payload, headers=headers)
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def stream_nvidia_response(payload: Dict[str, Any], headers: Dict[str, str]):
    async with httpx.AsyncClient(timeout=60.0) as async_client:
        async with async_client.stream(
            "POST", 
            f"{config.nvidia.base_url}/chat/completions", 
            json=payload, 
            headers=headers
        ) as response:
            if response.status_code != 200:
                error_detail = await response.aread()
                yield f"data: {json.dumps({'error': error_detail.decode()})}\n\n"
                return

            async for line in response.aiter_lines():
                if line:
                    yield f"{line}\n\n"

if __name__ == "__main__":
    uvicorn.run(app, host=config.server.host, port=config.server.port)
