from fastapi import APIRouter

from .auth.github_callback import router_callback
from .auth.login import router_login
from .auth.logout import router_logout
from .user.user import router_user
from .user.user_editing import router_user_editing

router_v1 = APIRouter()

# AUTH
router_v1.include_router(router_login, prefix="/v1/auth", tags=["auth"])
router_v1.include_router(router_callback, prefix="/v1/auth", tags=["auth"])
router_v1.include_router(router_logout, prefix="/v1/auth", tags=["auth"])

# USER
router_v1.include_router(router_user, prefix="/v1/user", tags=["user"])
router_v1.include_router(router_user_editing, prefix="/v1/user", tags=["user"])

__all__ = ["router_v1"]
