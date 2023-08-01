from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router_logout = APIRouter()


@router_logout.get("/logout")
async def github_logout():
    redirect_url = "/"
    response = RedirectResponse(redirect_url, status_code=302)
    response.delete_cookie("access_token")

    return response
