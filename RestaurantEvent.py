from events import Event


class RestaurantEvent:
    def __init__(
        self, reservation_number, restaurant_name, restaurant_address, time, party
    ):
        self.reservation_number = reservation_number
        self.restaurant_name = restaurant_name
        self.restaurant_address = restaurant_address
        self.party = party
        self.time = time

    def _get_start(self):
        return self.time

    def _get_summary(self):
        return f"Booking for {self.restaurant_name}"

    def _get_location(self):
        return self.restaurant_address

    def telegram(self):
        return f"""Would you like me to add the following *restaurant* to your calendar?
**Reservation Number:** {self.reservation_number}
**For:** {self.restaurant_name}
**At:** {self.time:%d %B %Y %H:%M}
"""
