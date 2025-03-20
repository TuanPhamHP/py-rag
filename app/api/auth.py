from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.chat_history import verify_user

router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    user_id: str
    password: str = None

class RegisterRequest(BaseModel):
    user_id: str
    password: str = None

# @router.post("/register")
# async def login(register_data: RegisterRequest):
#     result = await verify_user(register_data.user_id, register_data.password)
#     if not result["success"]:
#         raise HTTPException(status_code=401, detail=result["message"])
#     return {"access_token": result["access_token"], "token_type": "bearer"}

@router.post("/login")
async def login(login_data: LoginRequest):
    result = await verify_user(login_data.user_id, login_data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return {"access_token": result["access_token"], "token_type": "bearer"}