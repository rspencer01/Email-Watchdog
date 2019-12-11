from .Event import Event


class Appointment(Event):

    def _get_all_day(self) -> bool:
        return self.start.hour == 0

    def telegram(self) -> str:
        return f"""Would you like me to add the following *appointment* to your calendar?
**Regarding:** {self.summary}
**At:** {self.start:%d %B %Y %H:%M}
"""
