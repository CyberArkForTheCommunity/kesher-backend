# pylint: disable=no-name-in-module, no-self-argument
from pydantic import BaseModel, SecretStr

class RdsConnectionParams(BaseModel):
    port: int
    username: str  
    secret: SecretStr
    host: str