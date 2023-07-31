import logging
import os
from datetime import datetime, timedelta

import httpx
import jwt
import mysql.connector
from fastapi import FastAPI, HTTPException, Depends, status, Request, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.responses import RedirectResponse

from app.config import settings
from app.schemas.User import User

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GITHUB_LOGIN_ID = settings.GITHUB_LOGIN_ID
GITHUB_LOGIN_SECRET = settings.GITHUB_LOGIN_SECRET
JWT_PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), "private_key.pem")
JWT_ALGORITHM = settings.JWT_ALGORITHM

mydb = mysql.connector.connect(
    host=settings.MYSQL_INITDB_HOST,
    user=settings.MYSQL_INITDB_ROOT_USERNAME,
    password=settings.MYSQL_INITDB_ROOT_PASSWORD,
    database=settings.MYSQL_INITDB_DATABASE
)


def create_jwt_token(user_id):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }

    with open(JWT_PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()

    token = jwt.encode(payload, private_key, algorithm=JWT_ALGORITHM)
    return token


security = HTTPBearer()


def get_current_user(request: Request, authorization: str = Header(None)) -> None:
    print("Authorization Header:", authorization)

    if authorization is None or not authorization.startswith("Bearer "):
        return None

    access_token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(access_token, JWT_PRIVATE_KEY_PATH, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired.")
    except jwt.InvalidTokenError:
        print("Invalid token.")


def find_user_by_github_id(github_id):
    query = f"SELECT * FROM users WHERE {github_id} = %s"
    values = (github_id,)

    cursor = mydb.cursor()
    cursor.execute(query, values)

    result = cursor.fetchone()
    cursor.close()

    if result:
        user = {
            "id": result[0],
            "name": result[1],
            "email": result[2],
            "github_id": result[3],
        }
        return user
    else:
        return None


def save_github_user_to_database(user_data):
    global cursor

    query = "INSERT INTO users (username, name,avatar_url, profile_url,location, email, public_repos, public_gists, github_id, created_at, updated_at, followers, following) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    values = (
        user_data.get('login'),
        user_data.get('name'),
        user_data.get('avatar_url'),
        user_data.get('html_url'),
        user_data.get('location'),
        user_data.get('email'),
        user_data.get('repos_url'),
        user_data.get('gists_url'),
        user_data.get('id'),
        user_data.get('created_at'),
        user_data.get('updated_at'),
        user_data.get('followers'),
        user_data.get('following')
    )

    try:
        cursor = mydb.cursor()
        cursor.execute(query, values)
        mydb.commit()
        return cursor.lastrowid
    except mysql.connector.Error as error:
        print("Fehler beim Einfügen des Datensatzes:", error)
        return None
    finally:
        cursor.close()


@app.get("/v1/auth/github-login")
async def github_login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={GITHUB_LOGIN_ID}', status_code=302)


@app.get("/v1/auth/github-callback")
async def github_callback(code: str):
    # Code-Austausch gegen Zugriffstoken
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

    # Abrufen von Benutzerdaten von GitHub
    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'token {access_token}'})

        response = await client.get('https://api.github.com/user', headers=headers)

    github_user_data = response.json()

    if 'id' not in github_user_data:
        raise HTTPException(status_code=400, detail="Invalid GitHub user data")

    existing_user = find_user_by_github_id(github_user_data['id'])

    if existing_user is None:
        user_id = save_github_user_to_database(github_user_data)

        jwt_token = create_jwt_token(user_id)

        content = {"message": "Erfolgreich registriert und angemeldet",
                   "access_token": jwt_token.decode(),
                   "token_type": "bearer",
                   "user_id": user_id,
                   "github_data": github_user_data}

        response = JSONResponse(content=content)
        response.set_cookie(key="access_token", value=jwt_token, httponly=True)

        current_user = User(username=github_user_data.get("login"), name=github_user_data.get("name"),
                            token=jwt_token.decode())

        return response
    else:
        user_id = existing_user['id']

        jwt_token = create_jwt_token(user_id)

        content = {"message": "Erfolgreich angemeldet",
                   "access_token": jwt_token.decode(),
                   "token_type": "bearer",
                   "user_id": user_id,
                   "github_data": github_user_data}

        response = JSONResponse(content=content)
        response.set_cookie(key="access_token", value=jwt_token, httponly=True)

        current_user = User(username=github_user_data.get("login"), name=github_user_data.get("name"),
                            token=jwt_token.decode())

        return response


@app.get("/protected-route/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    logger.debug(f"Current user: {current_user}")

    if not current_user:
        logger.debug("Not authenticated")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    logger.debug("Authenticated")
    return {"message": "Hello, you are authenticated!"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.debug(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
