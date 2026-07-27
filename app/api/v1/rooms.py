from datetime import time as _time

from fastapi import APIRouter, Depends

from app.schemas.room import RoomResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["rooms"]
)

@router.get("/rooms", response_model=RoomResponse)
async def getRooms(
    buildingName: str,
    roomNumber: int,
    dayOfWeek: int,
    time: _time
):
    