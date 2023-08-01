import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.database import DatabaseConnection
from app.utils.jwt_utils import create_jwt_token

router_callback = APIRouter()

GITHUB_LOGIN_ID = settings.GITHUB_LOGIN_ID
GITHUB_LOGIN_SECRET = settings.GITHUB_LOGIN_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM


@router_callback.get("/github-callback")
async def github_callback(code: str):
    params = {
        'client_id': GITHUB_LOGIN_ID,
        'client_secret': GITHUB_LOGIN_SECRET,
        'code': code,
    }

    headers = {'Accept': 'application/json'}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url='https://github.com/login/oauth/access_token', params=params, headers=headers)

        response_json = response.json()
        access_token = response_json.get('access_token')

    if access_token is None:
        raise HTTPException(status_code=400, detail="Invalid GitHub API response")

    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'token {access_token}'})

        response = await client.get('https://api.github.com/user', headers=headers)

    github_user_data = response.json()

    if 'id' not in github_user_data:
        raise HTTPException(status_code=400, detail="Invalid GitHub user data")

    db = DatabaseConnection()

    user_columns = ['id', 'github_id', 'username', 'avatar_url']
    user_record = db.find_record_by_id('users', 'github_id', github_user_data['id'], user_columns)

    if user_record is None:
        user_data = {
            "username": github_user_data['login'],
            "name": github_user_data['name'],
            "github_id": github_user_data['id'],
            "profile_url": github_user_data['html_url'],
            "avatar_url": github_user_data['avatar_url'],
            "location": github_user_data['location'],
            "public_repos": github_user_data['repos_url'],
            "public_gists": github_user_data['gists_url'],
            "created_at": github_user_data['created_at'],
            "updated_at": github_user_data['updated_at'],
            "followers": github_user_data['followers'],
            "following": github_user_data['following'],
        }

        table_name = "users"
        column_names = list(user_data.keys())
        data = tuple(user_data.values())

        user_id = db.save_data_to_database(table_name, column_names, data)
        jwt_token = create_jwt_token(user_id)

        content = {"message": "Erfolgreich registriert und angemeldet",
                   "access_token": jwt_token.decode(),
                   "token_type": "bearer",
                   "user_id": user_id,
                   "github_data": github_user_data}

        response = JSONResponse(content=content)
        response.set_cookie(key="access_token", value=jwt_token, httponly=True)

        return response
    else:
        user_id = user_record['id']

        jwt_token = create_jwt_token(user_id)

        content = {"message": "Successfully logged in",
                   "access_token": jwt_token.decode(),
                   "token_type": "bearer",
                   "user_id": user_id,
                   "github_data": github_user_data}

        response = JSONResponse(content=content)
        response.set_cookie(key="access_token", value=jwt_token, httponly=True)

        return response
