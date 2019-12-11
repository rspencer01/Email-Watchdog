from .Event import Event


class LodgingEvent(Event):

    def __init__(
        self, reservation_number, lodging_name, lodging_address, check_in, check_out
    ):
        self.reservation_number = reservation_number
        self.lodging_name = lodging_name
        self.lodging_address = lodging_address
        self.check_in = check_in
        self.check_out = check_out

    def _get_summary(self):
        return f"Stay at {self.lodging_name}"

    def _get_start(self):
        return self.check_in

    def _get_end(self):
        return self.check_out

    def _get_location(self):
        return self.lodging_address

    def telegram(self):
        return f"""Would you like me to add the following *lodging reservation* to your calendar?
**Reservation Number:** {self.reservation_number}
**At:** {self.lodging_name}
**From:** {self.check_in:%d %B %Y}
**To:** {self.check_out:%d %B %Y}
"""
