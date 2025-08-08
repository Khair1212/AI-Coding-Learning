from fastapi import APIRouter
from app.api import auth, learning, assessment, admin, quiz_admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(quiz_admin.router, prefix="/admin/quizzes", tags=["quiz-admin"])

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}