# app/routes/v1/v1_routing.py

from fastapi import APIRouter

router_v2 = APIRouter(prefix="/v2")


@router_v2.get("/")
async def read_v1_root():
    return {"Hello": "Version 2"}
