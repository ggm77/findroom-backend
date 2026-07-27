from datetime import time as _time

from app.core.schedule import period_at
from app.schemas.room import RoomResponse
from app.services.timetable_store import timetable_store


def find_empty_rooms(buildingName: str | None, dayOfWeek: int, time: _time) -> list[RoomResponse]:
    period = period_at(time, timetable_store.max_period)

    rooms = timetable_store.all_rooms()
    if buildingName:
        rooms = [room for room in rooms if room[0] == buildingName]

    empty_rooms: list[RoomResponse] = []
    for building_name, room_number in rooms:
        occupied = period is not None and timetable_store.offering_at(
            building_name, room_number, dayOfWeek, period
        )
        if occupied:
            continue
        empty_rooms.append(
            RoomResponse(
                buildingName=building_name,
                roomNumber=room_number,
                classCode=None,
                className=None,
                professor=None,
                isEmpty=True,
            )
        )
    return empty_rooms
