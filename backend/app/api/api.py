from fastapi import APIRouter
from app.api import auth, learning, assessment

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}