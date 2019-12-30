"""Utilities for scanning incoming messages for events."""

import datetime

from nimbus.calendars import get_personal_calendar
from nimbus.emails import get_emails_since
from nimbus.notifications import add_notification, get_response
from nimbus.persistent.last import Last
from nimbus.process_mail import process_mail


def scan_for_event_invititaions() -> None:
    """Scan incoming emails for invitations to events and add them to a calendar."""
    check_since = Last.get_or_none(Last.key == "email_events")
    if check_since is not None:
        check_since = datetime.datetime.strptime(check_since.value, "%Y-%m-%d %H:%M:%S")
    else:
        check_since = datetime.datetime.now() - datetime.timedelta(days=1000)
        Last.create(
            key="email_events",
            value=(datetime.datetime.now() - datetime.timedelta(days=1000)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        ).save()

    try:
        seen = set(map(lambda x: x.strip(), open("seen").readlines()))
    except Exception:
        seen = set()

    emails = [email for email in get_emails_since(check_since) if email.uid not in seen]

    for email in emails:
        for r in process_mail(email):
            t = r.telegram()
            open("seen", "a").write("\n" + email.uid)
            if t is None:
                continue
            print(t)
            notification_id = add_notification(t, response_required=True)
            last_message = Last.get_or_none(Last.key == "email_events_message")
            if last_message is None:
                last_message = Last.create(key="email_events_message", value="")
            last_message.value = notification_id
            last_message.save()
            last_ical = Last.get_or_none(Last.key == "email_events_ical")
            if last_ical is None:
                last_ical = Last.create(key="email_events_ical", value="")
            last_ical.value = r.to_ical()
            last_ical.save()
            break

    check_since = Last.get(Last.key == "email_events")
    check_since.value = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_since.save()


def update() -> None:
    """Responds to users or scans for new invites."""
    last_message = Last.get_or_none(Last.key == "email_events_message")
    if last_message is None or last_message.value == "":
        scan_for_event_invititaions()
    else:
        response = get_response(last_message.value)
        if response == "yes":
            personal_calendar = get_personal_calendar()

            personal_calendar.add_event(Last.get(Last.key == "email_events_ical").value)
            last_message.delete_instance()
