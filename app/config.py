from pydantic import BaseSettings


class Settings(BaseSettings):
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str
    MYSQL_INITDB_HOST: str
    MYSQL_INITDB_ROOT_USERNAME: str
    MYSQL_INITDB_ROOT_PASSWORD: str
    MYSQL_INITDB_DATABASE: str
    GITHUB_LOGIN_ID: str
    GITHUB_LOGIN_SECRET: str

    class Config:
        env_file = './.env'


settings = Settings()
