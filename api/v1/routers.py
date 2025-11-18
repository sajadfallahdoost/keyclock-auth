from fastapi import APIRouter

from api.v1 import users

router = APIRouter()
router.include_router(users.router)



