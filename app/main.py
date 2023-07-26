import base64
import json
from datetime import datetime

import jwt
import mysql.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi import Response, status, Depends, HTTPException

from app import schemas, utils
from app.config import settings
from app.serializers.userSerializers import userResponseEntity

app = FastAPI()

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

mydb = mysql.connector.connect(
    host=settings.MYSQL_INITDB_HOST,
    user=settings.MYSQL_INITDB_ROOT_USERNAME,
    password=settings.MYSQL_INITDB_ROOT_PASSWORD,
    database=settings.MYSQL_INITDB_DATABASE
)


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def insert_one(data):
    global cursor
    query = "INSERT INTO users (name, email, role, created_at, updated_at, password, verified, secret_key) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        data['name'],
        data['email'],
        data['role'],
        data['created_at'],
        data['updated_at'],
        data['password'],
        data['verified'],
        data['secret_key']
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


def find_one(attribute, value):
    query = f"SELECT * FROM users WHERE {attribute} = %s"
    values = (value,)

    cursor = mydb.cursor()
    cursor.execute(query, values)

    result = cursor.fetchone()
    cursor.close()

    if result:
        user = {
            "id": result[0],
            "name": result[1],
            "email": result[2],
            "role": result[3],
            "created_at": result[4],
            "updated_at": result[5],
            "password": result[6],
            "verified": result[7],
            "secret_key": result[8]
        }
        return user
    else:
        return None


@app.post("/v1/healthcheck")
async def healthcheck():
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return {"message": "API is running", "database_connection": True}
    except Exception as err:
        return {"message": f"API is running, but there was an error connecting to the database: {err}",
                "database_connection": False}


@app.post("/v1/auth/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(payload: schemas.CreateUserSchema):
    user = find_one('email', payload.email.lower())

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    payload.password = utils.hash_password(payload.password)
    del payload.passwordConfirm

    private_key, public_key = generate_key_pair()

    payload.role = 'user'
    payload.verified = False
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at
    payload.secret_key = base64.b64encode(private_key).decode('utf-8')

    result_id = insert_one(payload.dict())
    new_user = find_one('id', result_id)

    print(result_id)
    print(new_user)

    return {"status": "success", "user": userResponseEntity(new_user)}


@app.post("/v1/auth/login")
async def login_user(payload: schemas.LoginUserSchema, response: Response, AuthJWT=Depends()):
    user = find_one('email', payload.email.lower())

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Incorrect email or password')

    if not utils.verify_password(payload.password, user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password')

    secrets_key = user.get("secret_key")

    payload_dict = payload.dict()

    access_token = jwt.encode(payload_dict, secrets_key, algorithm='HS256')

    refresh_token = jwt.encode(payload_dict, secrets_key, algorithm='HS256')

    response.set_cookie('access_token', access_token, max_age=ACCESS_TOKEN_EXPIRES_IN * 60, path='/', secure=True,
                        httponly=True, samesite='lax')
    response.set_cookie('refresh_token', refresh_token, max_age=REFRESH_TOKEN_EXPIRES_IN * 60, path='/', secure=True,
                        httponly=True, samesite='lax')

    return {'status': 'success', 'access_token': access_token}
