from datetime import time as _time

from fastapi import APIRouter

from app.schemas.room import RoomResponse
from app.services.empty_room_service import find_empty_rooms

router = APIRouter(
    prefix="/api/v1",
    tags=["emptyrooms"]
)

@router.get("/emptyrooms", response_model=list[RoomResponse])
async def getEmptyRooms(
    dayOfWeek: int,
    time: _time,
    buildingName: str | None = None,
):
    return find_empty_rooms(buildingName, dayOfWeek, time)
