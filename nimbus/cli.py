#!/usr/bin/env python3

import datetime

import click
from fabulous.color import bold
import gpx_trip
import yaml

import nimbus.travel
import nimbus.notifications
import nimbus.kimai

config = yaml.full_load(open("config.yaml"))


@click.group()
def travel():
    """All things to do with my movements."""


@click.command()
def current_position():
    """Where am I now?"""
    print(bold("You are at:"))
    print(bold("==========="))
    position = nimbus.travel.current_position()
    print("Place:      {}".format(position["location"]))
    print("Latitude:   {:.4f}".format(position["lat"]))
    print("Longitude:  {:.4f}".format(position["lon"]))
    print("Stationary: {}".format(position["stationary"]))


@click.command()
@click.argument("date", default=None)
def day(date):
    """What was yesterday like?

    Due to perculiarities, this only works after midday.
    TODO(robert) set the correct file so it works whenever.
    """
    if date is None:
        filename = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            config["tracking"]["historic_data_file"]
        )
    else:
        filename = datetime.datetime.strptime(date, "%Y-%m-%d").strftime(
            config["tracking"]["historic_data_file"]
        )

    info = gpx_trip.extract_info(
        open(filename).read(), predefined_stops=config["places"]
    )
    print(" " * 90, end="\r")
    for trip in info["trips"]:
        print(bold("Trip"))
        print(
            info["stops"][trip["from"]]["short_name"],
            "-",
            info["stops"][trip["to"]]["short_name"],
        )
        print(
            "{} - {}".format(
                trip["start"].strftime("%H:%M"), trip["end"].strftime("%H:%M")
            )
        )
        print()
    print(info)


@click.command()
def notifications():
    """Update the notifications"""
    nimbus.notifications.update()

@click.command()
def timesheet():
    """Collate information about timesheet"""
    nimbus.kimai.today()


travel.add_command(current_position)
travel.add_command(day)
