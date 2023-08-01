from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.config import settings

router_login = APIRouter()

GITHUB_LOGIN_ID = settings.GITHUB_LOGIN_ID


@router_login.get("/login")
async def github_login():
    redirect_url = f'https://github.com/login/oauth/authorize?client_id={GITHUB_LOGIN_ID}'

    return RedirectResponse(redirect_url, status_code=302)
