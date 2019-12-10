from datetime import datetime

from events import Event


class FlightEvent(Event):

    def __init__(
        self,
        reservation_number,
        flight_number,
        departure_airport_code,
        arrival_airport_code,
        departure_airport_name,
        arrival_airport_name,
        departure_time,
        arrival_time,
    ):
        self.reservation_number = reservation_number
        self.flight_number = flight_number
        self.departure_airport_code = departure_airport_code
        self.arrival_airport_code = arrival_airport_code
        self.departure_airport_name = departure_airport_name
        self.arrival_airport_name = arrival_airport_name
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    def _get_start(self) -> datetime:
        return self.departure_time

    def _get_end(self) -> datetime:
        return self.arrival_time

    def _get_summary(self) -> str:
        fc = self.departure_airport_code or self.departure_airport_name
        tc = self.arrival_airport_code or self.arrival_airport_name
        return "Flight {} -> {}".format(fc, tc)

    def telegram(self) -> str:
        return """Would you like me to add the following *flight* to your calendar?
**Reservation Number:** {reservation_number}
**From:** {frm}
**To:** {to}
**On:** {departure_time:%d %B %Y}
""".format(
            frm=self.departure_airport_name if self.departure_airport_name else self.departure_airport_code,
            to=self.arrival_airport_name if self.arrival_airport_name else self.arrival_airport_code,
            **self.__dict__
        )
