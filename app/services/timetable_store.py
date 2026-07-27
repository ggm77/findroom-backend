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

    def load(self, path: str | Path | None = None, encoding: str | None = None) -> None:
        resolved_path = Path(path) if path else settings.timetable_xls_path
        resolved_encoding = encoding or settings.timetable_encoding

        offerings = parse_timetable(resolved_path, encoding=resolved_encoding)

        by_class_code: dict[str, list[CourseOffering]] = defaultdict(list)
        by_room: dict[tuple[str, str], list[CourseOffering]] = defaultdict(list)
        for offering in offerings:
            by_class_code[offering.classCode].append(offering)
            if offering.buildingName and offering.roomText:
                by_room[(offering.buildingName, offering.roomText)].append(offering)

        self._offerings = offerings
        self._by_class_code = by_class_code
        self._by_room = by_room
        logger.info("Loaded %d course offerings from %s", len(offerings), resolved_path)

    @property
    def offerings(self) -> list[CourseOffering]:
        return self._offerings

    def offerings_by_class_code(self, class_code: str) -> list[CourseOffering]:
        return self._by_class_code.get(class_code, [])

    def offerings_by_room(self, building_name: str, room_text: str) -> list[CourseOffering]:
        return self._by_room.get((building_name, room_text), [])

    def __len__(self) -> int:
        return len(self._offerings)


timetable_store = TimetableStore()
