from fastapi import APIRouter, HTTPException

from app.services.heygen import heygen_service

router = APIRouter()


@router.get("/twins")
async def list_twins():
    """List available digital twins (HeyGen avatars)."""
    try:
        result = await heygen_service.list_avatars()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
