from fastapi import APIRouter

from app.db.database import DatabaseConnection

router_user = APIRouter()


@router_user.get("/user/{username}")
async def get_user_profile(username: str):
    db = DatabaseConnection()

    user_columns = ['username', 'name', 'location', 'profile_url']
    user_record = db.find_record_by_id('users', 'username', username, user_columns)

    if user_record is None:
        return {"message": "Benutzerprofil nicht gefunden."}
    else:
        return user_record
