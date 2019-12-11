"""Utilities to work with events."""

import hashlib
from datetime import datetime, timedelta
from typing import NamedTuple

import icalendar


class Event(NamedTuple):
    """An event in a user's life."""

    summary: str
    location: str
    start: datetime
    end: datetime = None
    all_day: bool = False

    def to_ical(self) -> str:
        """Construct an ical entry for this event."""
        cal = icalendar.Calendar()
        ev = icalendar.Event()
        if self.all_day:
            ev.add(
                "dtstart;value=date", self._get_start().strftime("%Y%m%d"), encode=False
            )
        else:
            ev.add("dtstart", self._get_start())
            if self._get_end() is not None:
                ev.add("dtend", self._get_end())
            else:
                ev.add("dtend", (self._get_start() + timedelta(hours=1)))
        ev.add("summary", self._get_summary())
        if self._get_location():
            ev.add("location", self._get_location())
        ev.add(
            "uid", "robert_spencer_bot_" + hashlib.sha256(str(self)).hexdigest()[:16]
        )
        cal.add_component(ev)
        return cal.to_ical()

    def _get_start(self) -> datetime:
        return self.start

    def _get_end(self) -> datetime:
        return self.end

    def _get_summary(self) -> str:
        return self.summary

    def _get_location(self) -> str:
        return self.location

    def _get_all_day(self) -> bool:
        return self.all_day
