import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from grpclib.server import Server
from grpclib.utils import graceful_exit
from promo_pb2 import (
    PromoRequest,
    PromoResponse,
    PromoListRequest,
    PromoListResponse,
    PromoUpdateRequest,
    PromoDeleteRequest,
    Empty
)
from promo_grpc import PromoServiceBase

class Promo:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        creator_id: str,
        discount_amount: float,
        code: str,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.discount_amount = discount_amount
        self.code = code
        self.created_at = created_at
        self.updated_at = updated_at

class PromoService(PromoServiceBase):
    def __init__(self):
        self.promos: List[Promo] = []

    async def CreatePromo(self, request: PromoRequest) -> PromoResponse:
        promo = Promo(
            id=str(uuid4()),
            name=request.name,
            description=request.description,
            creator_id=request.creator_id,
            discount_amount=request.discount_amount,
            code=request.code,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.promos.append(promo)
        return PromoResponse(
            id=promo.id,
            name=promo.name,
            description=promo.description,
            creator_id=promo.creator_id,
            discount_amount=promo.discount_amount,
            code=promo.code,
            created_at=promo.created_at.isoformat(),
            updated_at=promo.updated_at.isoformat()
        )

    async def ListPromos(self, request: PromoListRequest) -> PromoListResponse:
        start_idx = (request.page - 1) * request.limit
        end_idx = start_idx + request.limit
        items = self.promos[start_idx:end_idx]
        
        return PromoListResponse(
            items=[
                PromoResponse(
                    id=promo.id,
                    name=promo.name,
                    description=promo.description,
                    creator_id=promo.creator_id,
                    discount_amount=promo.discount_amount,
                    code=promo.code,
                    created_at=promo.created_at.isoformat(),
                    updated_at=promo.updated_at.isoformat()
                )
                for promo in items
            ],
            total=len(self.promos),
            page=request.page,
            limit=request.limit,
            pages=(len(self.promos) + request.limit - 1) // request.limit
        )

    async def GetPromo(self, request: PromoRequest) -> PromoResponse:
        promo = next((p for p in self.promos if p.id == request.id), None)
        if not promo:
            raise ValueError(f"Promo with id {request.id} not found")
        
        return PromoResponse(
            id=promo.id,
            name=promo.name,
            description=promo.description,
            creator_id=promo.creator_id,
            discount_amount=promo.discount_amount,
            code=promo.code,
            created_at=promo.created_at.isoformat(),
            updated_at=promo.updated_at.isoformat()
        )

    async def UpdatePromo(self, request: PromoUpdateRequest) -> PromoResponse:
        promo = next((p for p in self.promos if p.id == request.id), None)
        if not promo:
            raise ValueError(f"Promo with id {request.id} not found")
        
        if request.name is not None:
            promo.name = request.name
        if request.description is not None:
            promo.description = request.description
        if request.discount_amount is not None:
            promo.discount_amount = request.discount_amount
        if request.code is not None:
            promo.code = request.code
        
        promo.updated_at = datetime.utcnow()
        
        return PromoResponse(
            id=promo.id,
            name=promo.name,
            description=promo.description,
            creator_id=promo.creator_id,
            discount_amount=promo.discount_amount,
            code=promo.code,
            created_at=promo.created_at.isoformat(),
            updated_at=promo.updated_at.isoformat()
        )

    async def DeletePromo(self, request: PromoDeleteRequest) -> Empty:
        promo = next((p for p in self.promos if p.id == request.id), None)
        if not promo:
            raise ValueError(f"Promo with id {request.id} not found")
        
        self.promos.remove(promo)
        return Empty()

async def main():
    server = Server([PromoService()])
    with graceful_exit([server]):
        await server.start('0.0.0.0', 50051)
        print('Promo service started on port 50051')
        await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
