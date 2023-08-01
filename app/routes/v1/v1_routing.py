from fastapi import APIRouter

from .auth.github_callback import router_callback
from .auth.login import router_login
from .auth.logout import router_logout

router_v1 = APIRouter()

router_v1.include_router(router_login, prefix="/v1/auth", tags=["auth"])
router_v1.include_router(router_callback, prefix="/v1/auth", tags=["auth"])
router_v1.include_router(router_logout, prefix="/v1/auth", tags=["auth"])

__all__ = ["router_v1"]
