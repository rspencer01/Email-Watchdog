import datetime
import os

import mailparser

from nimbus import process_mail
from nimbus.events import Appointment


def test_mail_appointment_01():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    em = mailparser.parse_from_file(
        os.path.join(this_dir, "Re: Tutorial Appointment.eml")
    )
    assert process_mail.process_mail(em) == [
        Appointment(
            summary="Meet with Rebecca Kippax",
            location=None,
            start=datetime.datetime(2019, 10, 29, 12, 40),
            end=None,
            all_day=False,
        )
    ]
