import logging
import os
from datetime import datetime, timedelta

import jwt

JWT_PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "secrets", "private_key.pem")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_jwt_token(user_id):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=15),
    }

    with open(JWT_PRIVATE_KEY_PATH, "rb") as f:
        private_key = f.read()

    logger.debug("Private key file opened and read successfully.")

    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        logger.info("JWT token created successfully.")
        return token
    except Exception as e:
        logger.error("Error creating JWT token: %s", e)
        raise
