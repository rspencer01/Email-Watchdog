from icalendar import Calendar, Event
import hashlib


class LodgingEvent:
    def __init__(
        self, reservation_number, lodging_name, lodging_address, check_in, check_out
    ):
        self.reservation_number = reservation_number
        self.lodging_name = lodging_name
        self.lodging_address = lodging_address
        self.check_in = check_in
        self.check_out = check_out

    def ical(self):
        cal = Calendar()
        ev = Event()
        ev.add("dtstart", self.check_in)
        ev.add("dtend", self.check_out)
        ev.add("summary", "Staying at {}".format(self.lodging_name))
        ev.add("location", self.lodging_address)
        ev.add(
            "uid",
            "robert_spencer_bot_"
            + hashlib.sha256(str(self.__dict__).encode("utf-8")).hexdigest()[:16],
        )
        cal.add_component(ev)
        return cal.to_ical()
