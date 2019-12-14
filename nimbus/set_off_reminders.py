"""Sends reminders when you need to go to an event."""

import logging
from datetime import datetime, timedelta

from geopy import geocoders

import openrouteservice

import yaml

from .calendars import get_next_event
from .notifications import add_notification
from .persistent.last import Last
from .travel import current_position

config = yaml.full_load(open("config.yaml"))


def get_set_off_reminder() -> None:
    """Send reminder if one is due."""
    position = current_position()
    logging.warn("Current position %s", position)
    event = get_next_event()
    logging.warn("Next event %s", event)
    if event is None or position is None:
        return
    geocoder = geocoders.Photon()
    destination = geocoder.geocode(
        event["location"], location_bias=(position["lat"], position["lon"])
    )
    logging.warn("Destination %s %s", destination.latitude, destination.longitude)
    route_client = openrouteservice.Client(
        key=config['tracking']['orskey']
    )
    travel_time = route_client.directions(
        (
            (position["lon"], position["lat"]),
            (destination.longitude, destination.latitude),
        ),
        profile="foot-walking",
    )["routes"][0]["summary"]["duration"]
    logging.warn("Travel time %s", travel_time)

    last_run = Last.get_or_none(Last.key == "set_off_reminder")
    if last_run is None:
        last_run = Last.create(
            key="set_off_reminder", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    last_run_time = datetime.strptime(last_run.value, "%Y-%m-%d %H:%M:%S")

    warn_time = event["start"].replace(tzinfo=None) - timedelta(seconds=travel_time)
    logging.warn("Warn time %s", warn_time)
    immediate_message = "To get to **{}** for **{}** by **{}** you will need to leave now.".format(
        event["location"], event["title"], event["start"].strftime("%H:%M")
    )
    if last_run_time < warn_time and warn_time < datetime.now():
        add_notification(immediate_message)
    last_run.value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_run.save()
