from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: str = ""
    password: str = ""
    invite_code: str = ""


class LoginResponse(BaseModel):
    token: str = ""
    expires_at: int = 0
    error: str = ""


class PublicKeyResponse(BaseModel):
    public_key: str = ""
    error: str = ""
