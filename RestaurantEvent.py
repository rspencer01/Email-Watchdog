class RestaurantEvent:
    def __init__(
        self, reservation_number, restaurant_name, restaurant_address, time, party
    ):
        self.reservation_number = reservation_number
        self.restaurant_name = restaurant_name
        self.restaurant_address = restaurant_address
        self.party = party
        self.time = time
