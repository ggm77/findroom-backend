from datetime import time as _time

from app.core.schedule import period_at
from app.schemas.room import RoomResponse
from app.services.timetable_store import timetable_store


def get_room_status(buildingName: str, roomNumber: int, dayOfWeek: int, time: _time) -> RoomResponse:
    period = period_at(time, timetable_store.max_period)
    offering = (
        timetable_store.offering_at(buildingName, roomNumber, dayOfWeek, period)
        if period is not None
        else None
    )

    if offering is None:
        return RoomResponse(
            buildingName=buildingName,
            roomNumber=roomNumber,
            classCode=None,
            className=None,
            professor=None,
            isEmpty=True,
        )

    return RoomResponse(
        buildingName=buildingName,
        roomNumber=roomNumber,
        classCode=offering.classCode,
        className=offering.className,
        professor=offering.professor,
        isEmpty=False,
    )
