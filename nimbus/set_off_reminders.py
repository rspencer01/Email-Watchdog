"""Sends reminders when you need to go to an event."""

import io
import logging
from datetime import datetime, timedelta

import cairo

from geopy import geocoders

import geotiler

import openrouteservice

import polyline

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
    route_client = openrouteservice.Client(key=config["tracking"]["orskey"])
    route = route_client.directions(
        (
            (position["lon"], position["lat"]),
            (destination.longitude, destination.latitude),
        ),
        profile="foot-walking",
    )["routes"][0]
    travel_time = route["summary"]["duration"]
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
        add_notification(immediate_message, photo=get_route_image(route))
    last_run.value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_run.save()


def get_route_image(route) -> bytes:
    mm = geotiler.Map(extent=route["bbox"], size=(768, 768))
    width, height = mm.size

    img = geotiler.render_map(mm)

    buff = bytearray(img.convert("RGBA").tobytes("raw", "BGRA"))
    surface = cairo.ImageSurface.create_for_data(
        buff, cairo.FORMAT_ARGB32, width, height
    )
    cr = cairo.Context(surface)
    pts = [mm.rev_geocode(pt[::-1]) for pt in polyline.decode(route["geometry"])]
    cr.set_source_rgba(0.0, 0.5, 1.0, 0.5)

    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_width(8)
    cr.move_to(*pts[0])
    for pt in pts:
        cr.line_to(*pt)
    cr.stroke()
    bt = io.BytesIO()
    surface.write_to_png(bt)
    bt.seek(0)
    return bt.read()
