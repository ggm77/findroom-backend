from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from lxml import html
from lxml.html import HtmlElement

DAY_NAME_TO_INDEX = {
    "월": 0,
    "화": 1,
    "수": 2,
    "목": 3,
    "금": 4,
    "토": 5,
    "일": 6,
}

_SESSION_RE = re.compile(r"([월화수목금토일])(\d+)")
_BUILDING_RE = re.compile(r"^([A-Za-z]+)\s*(.*)$")
_LEADING_INT_RE = re.compile(r"^(\d+)")
_CLASS_NAME_RE = re.compile(r"^(.*?)\(([^()]*)\)\s*$")

SKIPPED_BUILDINGS = {"HCA", "EBEN"}
_ANH_AUDITORIUM_ROOM_NUMBER = 0


@dataclass(frozen=True)
class ClassSession:
    dayOfWeek: int
    dayName: str
    period: int


@dataclass
class CourseOffering:
    category: str
    classCode: str
    section: str
    className: str
    classNameEn: str | None
    credit: float | None
    campus: str | None
    courseType: str | None
    professor: str | None
    buildingName: str | None
    roomText: str | None
    roomNumber: int | None
    capacity: int | None
    enrolled: int | None
    sessions: list[ClassSession] = field(default_factory=list)


def _clean(text: str | None) -> str:
    if text is None:
        return ""
    return text.replace("\xa0", " ").strip()


def _parse_class_name(raw: str) -> tuple[str, str | None]:
    cleaned = _clean(raw)
    match = _CLASS_NAME_RE.match(cleaned)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return cleaned, None


def _parse_credit(raw: str) -> float | None:
    cleaned = _clean(raw)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_campus_and_professor(cell: HtmlElement) -> tuple[str | None, str | None, str | None]:
    fonts = cell.xpath(".//font")
    professor = _clean(fonts[0].text_content()) if fonts else ""

    header_nodes = cell.xpath("./text()")
    header_text = _clean(header_nodes[0]) if header_nodes else ""
    parts = header_text.split()
    campus = parts[0] if parts else None
    course_type = parts[1] if len(parts) > 1 else None

    return campus, course_type, professor or None


def _parse_sessions(raw: str) -> list[ClassSession]:
    cleaned = _clean(raw)
    return [
        ClassSession(dayOfWeek=DAY_NAME_TO_INDEX[day_char], dayName=day_char, period=int(period))
        for day_char, period in _SESSION_RE.findall(cleaned)
    ]


def _parse_room(raw: str) -> tuple[str | None, str | None, int | None]:
    cleaned = _clean(raw)
    if not cleaned:
        return None, None, None

    match = _BUILDING_RE.match(cleaned)
    if not match:
        return None, cleaned, None

    building_name, rest = match.group(1), match.group(2).strip()
    room_number_match = _LEADING_INT_RE.match(rest)
    room_number = int(room_number_match.group(1)) if room_number_match else None

    if building_name == "ANH" and rest.lower() == "auditorium":
        room_number = _ANH_AUDITORIUM_ROOM_NUMBER

    return building_name, cleaned, room_number


def _parse_int(raw: str) -> int | None:
    cleaned = _clean(raw)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def parse_timetable(path: str | Path, encoding: str = "cp949") -> list[CourseOffering]:
    """개설시간표.xls(실제로는 HTML 테이블) 파일을 파싱해 CourseOffering 목록으로 반환한다."""
    path = Path(path)
    raw_html = path.read_text(encoding=encoding, errors="replace")
    tree = html.fromstring(raw_html)
    rows = tree.xpath("//table//tr")[1:]  # 첫 행은 헤더

    offerings: list[CourseOffering] = []
    for row in rows:
        cells = row.xpath("./td")
        if len(cells) < 10:
            continue

        building_name, room_text, room_number = _parse_room(cells[7].text_content())
        if building_name in SKIPPED_BUILDINGS:
            continue

        class_name, class_name_en = _parse_class_name(cells[3].text_content())
        campus, course_type, professor = _parse_campus_and_professor(cells[5])

        offerings.append(
            CourseOffering(
                category=_clean(cells[0].text_content()),
                classCode=_clean(cells[1].text_content()),
                section=_clean(cells[2].text_content()),
                className=class_name,
                classNameEn=class_name_en,
                credit=_parse_credit(cells[4].text_content()),
                campus=campus,
                courseType=course_type,
                professor=professor,
                buildingName=building_name,
                roomText=room_text,
                roomNumber=room_number,
                capacity=_parse_int(cells[8].text_content()),
                enrolled=_parse_int(cells[9].text_content()),
                sessions=_parse_sessions(cells[6].text_content()),
            )
        )

    return offerings
