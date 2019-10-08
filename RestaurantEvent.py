from icalendar import Calendar, Event
import hashlib
import datetime


class RestaurantEvent:
    def __init__(
        self, reservation_number, restaurant_name, restaurant_address, time, party
    ):
        self.reservation_number = reservation_number
        self.restaurant_name = restaurant_name
        self.restaurant_address = restaurant_address
        self.party = party
        self.time = time

    def ical(self):
        cal = Calendar()
        ev = Event()
        ev.add("dtstart", self.time)
        ev.add("dtend", self.time + datetime.timedelta(hours=1))
        ev.add("summary", "Booking for {}".format(self.restaurant_name))
        ev.add("location", self.restaurant_address)
        ev.add(
            "uid",
            "robert_spencer_bot_"
            + hashlib.sha256(str(self.__dict__).encode("utf-8")).hexdigest()[:16],
        )
        cal.add_component(ev)
        return cal.to_ical()

    def telegram(self):
        return """Would you like me to add the following *restaurant* to your calendar?
**Reservation Number:** {reservation_number}
**For:** {restaurant_name}
**At:** {time:%d %B %Y %H:%M}
""".format(
            **self.__dict__
        )
