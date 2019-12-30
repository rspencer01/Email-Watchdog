"""Utilities for calendars."""

import datetime

import caldav

import icalendar

import yaml

config = yaml.full_load(open("config.yaml"))


def get_personal_calendar():
    """Find the personal calendar for the user."""
    personal_calendar_config = config["calendars"][0]

    client = caldav.DAVClient(
        "https://{username}:{password}@{url}".format(**personal_calendar_config)
    )
    principal = client.principal()
    calendars = principal.calendars()
    return [i for i in calendars if i.name == personal_calendar_config["name"]][0]


def get_next_event() -> None:
    """Find the next event for the user."""
    personal_calendar = get_personal_calendar()
    midnight = datetime.datetime.now().replace(
        hour=0, minute=0, second=0
    ) + datetime.timedelta(days=1)
    first = None
    for i in personal_calendar.date_search(datetime.datetime.now(), midnight):
        event = icalendar.Event.from_ical(i.data).walk()[1]
        if first is None or first.get("dtstart").dt > event.get("dtstart").dt:
            first = event
    if first is None:
        return None
    return {
        "title": str(first.get("summary")),
        "start": first.get("dtstart").dt,
        "location": str(first.get("location")),
    }
