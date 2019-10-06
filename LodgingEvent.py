class LodgingEvent:
    def __init__(
        self, reservation_number, lodging_name, lodging_address, check_in, check_out
    ):
        self.reservation_number = reservation_number
        self.lodging_name = lodging_name
        self.check_in = check_in
        self.check_out = check_out
