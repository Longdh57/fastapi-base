from fastapi import APIRouter

from app.api import api_user, api_login

router = APIRouter()

router.include_router(api_login.router, tags=["login"], prefix="/login")
router.include_router(api_user.router, tags=["user"], prefix="/users")
