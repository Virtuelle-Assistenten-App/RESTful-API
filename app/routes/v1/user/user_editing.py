import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.utils.jwt_utils import get_jwt_private_key

router_user_editing = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_token(token: str = Depends(oauth2_scheme), private_key_func=get_jwt_private_key):
    print("Token:", token)
    private_key = private_key_func()
    print("Private Key:", private_key)
    try:
        payload = jwt.decode(token, private_key, algorithms=["RS256"])
        print("Decoded Payload:", payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ist abgelaufen")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültiger Token")


@router_user_editing.get("/edit/{username}")
async def update_user_profile(username: str, token_payload: dict = Depends(verify_token)):
    if token_payload["sub"] != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Keine Berechtigung, dieses Profil zu bearbeiten")
    return {"message": "Benutzerprofil erfolgreich aktualisiert.", "username": username}
