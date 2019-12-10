from icalendar import Calendar, Event
import hashlib
import datetime


class Appointment:
    def __init__(self, regarding, time, location):
        self.regarding = regarding
        self.time = time
        self.location = location

    def ical(self):
        cal = Calendar()
        ev = Event()
        if self.time.hour != 0:
            ev.add("dtstart", self.time)
            ev.add("dtend", (self.time + datetime.timedelta(hours=1)))
        else:
            ev.add("dtstart;value=date", self.time.strftime("%Y%m%d"), encode=False)
        ev.add("summary", self.regarding)
        ev.add("location", self.location)
        ev.add(
            "uid",
            "robert_spencer_bot_"
            + hashlib.sha256(str(self.__dict__).encode("utf-8")).hexdigest()[:16],
        )
        cal.add_component(ev)
        return cal.to_ical()

    def telegram(self):
        return """Would you like me to add the following *appointment* to your calendar?
**Regarding:** {regarding}
**At:** {time:%d %B %Y %H:%M}
""".format(
            **self.__dict__
        )

    def __repr__(self):
      return "<Appointment {}>".format(self.__dict__)
