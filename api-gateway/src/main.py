from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from typing import Any, Dict

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
API_PREFIX = "/api/v1"

app = FastAPI(title="API Gateway", description="API Gateway for microservices architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http_client = httpx.AsyncClient(base_url=USER_SERVICE_URL, timeout=30.0)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

async def proxy_request(request: Request, path: str) -> Response:
    method = request.method
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    params = dict(request.query_params)
    
    target_url = f"{path}"
    
    try:
        response = await http_client.request(
            method=method,
            url=target_url,
            headers=headers,
            params=params,
            content=body
        )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error communicating with user service: {str(exc)}"
        )

@app.post(f"{API_PREFIX}/auth/register")
async def register(request: Request):
    return await proxy_request(request, f"{API_PREFIX}/auth/register")

@app.post(f"{API_PREFIX}/auth/login")
async def login(request: Request):
    return await proxy_request(request, f"{API_PREFIX}/auth/login")

@app.get(f"{API_PREFIX}/users/profile")
async def get_profile(request: Request):
    return await proxy_request(request, f"{API_PREFIX}/users/profile")

@app.put(f"{API_PREFIX}/users/profile")
async def update_profile(request: Request):
    return await proxy_request(request, f"{API_PREFIX}/users/profile")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
