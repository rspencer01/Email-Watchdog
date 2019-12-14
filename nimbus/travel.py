"""Utilities for position, travel and transit."""

from datetime import datetime

from geopy import geocoders

import requests

import yaml

config = yaml.full_load(open("config.yaml"))


def current_position() -> None:
    """Obtain information about the user's current position."""
    session = config["tracking"]["session"]
    device = config["tracking"]["device"]
    response = requests.get(config["tracking"]["url"] + session, params={"limit": 1})
    points = response.json()[session][device]["points"]
    if points == []:
        return None
    for point in points:
        point["timestamp"] = datetime.fromtimestamp(point["timestamp"])
    if (datetime.now() - points[-1]["timestamp"]).seconds > 120 * 3600:
        return None

    geocoder = geocoders.Photon()
    return {
        "lat": points[-1]["lat"],
        "lon": points[-1]["lon"],
        "stationary": points[-1]["speed"] < 0.2,
        "location": geocoder.reverse("{lat}, {lon}".format(**points[-1])).address,
    }
