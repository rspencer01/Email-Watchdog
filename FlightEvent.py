class FlightEvent:
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
