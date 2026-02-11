from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # JWT
    JWT_EXPIRATION: int = 15  # minutes
    JWT_KEY: str = "very-not-secure-jwt-key"
    JWT_ALG: str = "HS256"

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PWD: str = "admin"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgresdb"

    @computed_field
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        """
        Construct PostgreSQL connection URI.
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PWD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
