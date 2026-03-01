import json
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import uvicorn

from config_loader import config
from utils import trim_messages, count_tokens_for_embedding

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
    
    # Remove tool/function calling parameters that NVIDIA API doesn't support
    for key in ["tools", "tool_choice", "functions", "function_call", "parallel_tool_calls"]:
        nvidia_payload.pop(key, None)
    
    # Remove tool_call_id and function_call from individual messages
    cleaned_messages = []
    for msg in nvidia_payload["messages"]:
        cleaned_msg = {k: v for k, v in msg.items() if k not in ["tool_calls", "tool_call_id", "function_call", "name"] or k == "name" and msg.get("role") != "tool"}
        # Skip tool role messages entirely
        if msg.get("role") == "tool":
            continue
        cleaned_messages.append(cleaned_msg)
    nvidia_payload["messages"] = cleaned_messages
    
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

@app.post("/v1/embeddings")
async def embeddings(request: Request, token: str = Depends(verify_token)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    input_texts = body.get("input")
    model = body.get("model", config.nvidia.default_embedding_model)

    if not input_texts:
        raise HTTPException(status_code=400, detail="'input' field is required")

    # Ensure input_texts is a list of strings
    if isinstance(input_texts, str):
        input_texts = [input_texts]
    elif not isinstance(input_texts, list) or not all(isinstance(i, str) for i in input_texts):
        raise HTTPException(status_code=400, detail="'input' must be a string or a list of strings")

    nvidia_payload = {
        "input": input_texts,
        "model": model
    }

    headers = {
        "Authorization": f"Bearer {config.nvidia.api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = await client.post("/embeddings", json=nvidia_payload, headers=headers)
        nvidia_response = response.json()

        # Transform NVIDIA response to OpenAI compatible format
        openai_data = []
        for i, item in enumerate(nvidia_response.get("data", [])):
            openai_data.append({
                "object": "embedding",
                "embedding": item["embedding"],
                "index": i
            })
        
        # Calculate token usage
        prompt_tokens = count_tokens_for_embedding(input_texts, model)

        openai_response = {
            "object": "list",
            "data": openai_data,
            "model": model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "total_tokens": prompt_tokens
            }
        }
        return JSONResponse(content=openai_response, status_code=response.status_code)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host=config.server.host, port=config.server.port)
