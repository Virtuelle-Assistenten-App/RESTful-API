from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.routing import Route

from app.routes import register_routers

app = FastAPI()

register_routers(app)


@app.get("/routes")
async def print_loaded_routes():
    routes_list = []
    for route in app.routes:
        if isinstance(route, Route):
            methods = list(route.methods)
            routes_list.append({"route-name": route.name, "methods": methods, "path": route.path})

    return JSONResponse(content={"message": "All routes loaded successfully", "routes": routes_list})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(content={"detail": "Validation Error"}, status_code=400)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(content={"detail": "Oops! Something went wrong."}, status_code=exc.status_code)
