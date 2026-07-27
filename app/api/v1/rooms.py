from datetime import time as _time

from fastapi import APIRouter

from app.schemas.room import RoomResponse
from app.services.room_service import get_room_status

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
    return get_room_status(buildingName, roomNumber, dayOfWeek, time)
