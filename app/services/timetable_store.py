from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from app.core.config import settings
from app.services.timetable_parser import CourseOffering, parse_timetable

logger = logging.getLogger(__name__)


class TimetableStore:
    """파싱된 시간표를 메모리에 들고 있다가 서비스 전반에서 재사용하기 위한 저장소."""

    def __init__(self) -> None:
        self._offerings: list[CourseOffering] = []
        self._by_class_code: dict[str, list[CourseOffering]] = defaultdict(list)
        self._by_room: dict[tuple[str, str], list[CourseOffering]] = defaultdict(list)
        self._session_index: dict[tuple[str, int, int, int], CourseOffering] = {}
        self._rooms: list[tuple[str, int]] = []
        self._max_period: int = 0

    def load(self, path: str | Path | None = None, encoding: str | None = None) -> None:
        resolved_path = Path(path) if path else settings.timetable_xls_path
        resolved_encoding = encoding or settings.timetable_encoding

        offerings = parse_timetable(resolved_path, encoding=resolved_encoding)

        by_class_code: dict[str, list[CourseOffering]] = defaultdict(list)
        by_room: dict[tuple[str, str], list[CourseOffering]] = defaultdict(list)
        session_index: dict[tuple[str, int, int, int], CourseOffering] = {}
        rooms: set[tuple[str, int]] = set()
        max_period = 0
        for offering in offerings:
            by_class_code[offering.classCode].append(offering)
            if offering.buildingName and offering.roomText:
                by_room[(offering.buildingName, offering.roomText)].append(offering)
            if offering.buildingName and offering.roomNumber is not None:
                rooms.add((offering.buildingName, offering.roomNumber))
                for session in offering.sessions:
                    session_index[
                        (offering.buildingName, offering.roomNumber, session.dayOfWeek, session.period)
                    ] = offering
                    max_period = max(max_period, session.period)

        self._offerings = offerings
        self._by_class_code = by_class_code
        self._by_room = by_room
        self._session_index = session_index
        self._rooms = sorted(rooms)
        self._max_period = max_period
        logger.info("Loaded %d course offerings from %s", len(offerings), resolved_path)

    @property
    def offerings(self) -> list[CourseOffering]:
        return self._offerings

    @property
    def max_period(self) -> int:
        return self._max_period

    def offerings_by_class_code(self, class_code: str) -> list[CourseOffering]:
        return self._by_class_code.get(class_code, [])

    def offerings_by_room(self, building_name: str, room_text: str) -> list[CourseOffering]:
        return self._by_room.get((building_name, room_text), [])

    def all_rooms(self) -> list[tuple[str, int]]:
        return self._rooms

    def offering_at(
        self, building_name: str, room_number: int, day_of_week: int, period: int
    ) -> CourseOffering | None:
        return self._session_index.get((building_name, room_number, day_of_week, period))

    def __len__(self) -> int:
        return len(self._offerings)


timetable_store = TimetableStore()
