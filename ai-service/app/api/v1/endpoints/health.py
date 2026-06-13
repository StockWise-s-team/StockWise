from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
@router.get("/advisor/health")
async def health_check():
    return {"status": "ok"}
