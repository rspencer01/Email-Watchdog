"""Utilities for position, travel and transit."""

from datetime import datetime

from geopy import distance, exc, geocoders

import requests

import yaml

config = yaml.full_load(open("config.yaml"))


def current_position() -> None:
    """Obtain information about the user's current position."""
    session = config["tracking"]["session"]
    device = config["tracking"]["device"]
    locations = config["places"]
    response = requests.get(config["tracking"]["last_position_url"] + session)
    last_point = response.json()[session][device]
    last_point["timestamp"] = datetime.fromtimestamp(last_point["timestamp"])
    if (datetime.now() - last_point["timestamp"]).seconds > 120 * 3600:
        return None

    for location in locations:
        if (
            distance.distance(
                (location["lat"], location["lon"]),
                (last_point["lat"], last_point["lon"]),
            ).meters
            < 30
        ):
            location_name = location["name"]
            break
    else:
        geocoder = geocoders.Photon()
        try:
            location_name = geocoder.reverse(
                "{lat}, {lon}".format(**last_point)
            ).address
        except exc.GeocoderTimedOut:
            location_name = None

    return {
        "lat": last_point["lat"],
        "lon": last_point["lon"],
        "stationary": last_point["speed"] < 0.2,
        "location": location_name,
    }
