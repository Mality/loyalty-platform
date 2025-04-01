from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from typing import Any, Dict
from grpclib.client import Channel
from promo_pb2 import PromoRequest, PromoListRequest, PromoUpdateRequest, PromoDeleteRequest
from promo_grpc import PromoServiceStub

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
PROMO_SERVICE_HOST = os.getenv("PROMO_SERVICE_HOST", "promo-service")
PROMO_SERVICE_PORT = int(os.getenv("PROMO_SERVICE_PORT", "50051"))
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
promo_channel = Channel(PROMO_SERVICE_HOST, PROMO_SERVICE_PORT)
promo_client = PromoServiceStub(promo_channel)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    promo_channel.close()

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

@app.post(f"{API_PREFIX}/promos")
async def create_promo(request: Request):
    try:
        body = await request.json()
        promo_request = PromoRequest(
            name=body["name"],
            description=body["description"],
            creator_id=body["creatorId"],
            discount_amount=body["discountAmount"],
            code=body["code"]
        )
        response = await promo_client.CreatePromo(promo_request)
        return Response(
            content=response.SerializeToString(),
            status_code=status.HTTP_201_CREATED,
            media_type="application/json"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating promo: {str(exc)}"
        )

@app.get(f"{API_PREFIX}/promos")
async def list_promos(request: Request):
    try:
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        promo_request = PromoListRequest(page=page, limit=limit)
        response = await promo_client.ListPromos(promo_request)
        return Response(
            content=response.SerializeToString(),
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing promos: {str(exc)}"
        )

@app.get(f"{API_PREFIX}/promos/{{promo_id}}")
async def get_promo(promo_id: str):
    try:
        promo_request = PromoRequest(id=promo_id)
        response = await promo_client.GetPromo(promo_request)
        return Response(
            content=response.SerializeToString(),
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting promo: {str(exc)}"
        )

@app.put(f"{API_PREFIX}/promos/{{promo_id}}")
async def update_promo(promo_id: str, request: Request):
    try:
        body = await request.json()
        promo_request = PromoUpdateRequest(
            id=promo_id,
            name=body.get("name"),
            description=body.get("description"),
            discount_amount=body.get("discountAmount"),
            code=body.get("code")
        )
        response = await promo_client.UpdatePromo(promo_request)
        return Response(
            content=response.SerializeToString(),
            status_code=status.HTTP_200_OK,
            media_type="application/json"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating promo: {str(exc)}"
        )

@app.delete(f"{API_PREFIX}/promos/{{promo_id}}")
async def delete_promo(promo_id: str):
    try:
        promo_request = PromoDeleteRequest(id=promo_id)
        await promo_client.DeletePromo(promo_request)
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting promo: {str(exc)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
