from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host : str
    db_port : str
    db_user : str
    db_pass : str
    db_name : str
    jwt_secret_key : str
    jwt_algorithm : str
    jwt_access_token_exp_min : int

    class Config:
        env_file = ".env"

settings = Settings()