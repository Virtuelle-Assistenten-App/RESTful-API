from .v1.v1_routing import router_v1
from .v2.v2 import router_v2

routers = [router_v1, router_v2]


def register_routers(app):
    for router in routers:
        app.include_router(router)


__all__ = ["router_v1", "router_v2"]
