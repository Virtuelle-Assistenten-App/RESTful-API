def userEntity(user) -> dict:
    return {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "verified": user["verified"],
        "password": user["password"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "secret_key": user["secret_key"],
    }


def userResponseEntity(user) -> dict:
    return {
        "id": str(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "secret_key": user["secret_key"],
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["id"]),
        "name": user["name"],
        "email": user["email"]
    }


def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
