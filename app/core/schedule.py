from __future__ import annotations

from datetime import datetime, time, timedelta

PERIOD_1_START = time(9, 0)
CLASS_MINUTES = 75
BREAK_MINUTES = 15
SLOT_MINUTES = CLASS_MINUTES + BREAK_MINUTES


def period_bounds(period: int) -> tuple[time, time]:
    """주어진 교시(1부터 시작)의 시작/종료 시각을 반환한다."""
    start = datetime.combine(datetime.min, PERIOD_1_START) + timedelta(minutes=(period - 1) * SLOT_MINUTES)
    end = start + timedelta(minutes=CLASS_MINUTES)
    return start.time(), end.time()


def period_at(target: time, max_period: int) -> int | None:
    """주어진 시각이 속한 교시를 반환한다. 쉬는 시간 등 수업이 없는 시각이면 None."""
    for period in range(1, max_period + 1):
        start, end = period_bounds(period)
        if start <= target < end:
            return period
    return None
