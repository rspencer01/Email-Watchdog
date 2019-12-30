import logging
import sys

from bs4 import BeautifulSoup

import dateparser.search

import dateutil.parser

import extruct

import mailparser

import nltk
from nltk.tag.stanford import StanfordNERTagger

from .Notification import Notification
from .events import Appointment, FlightEvent, LodgingEvent, RestaurantEvent


st = StanfordNERTagger(
    "stanford_ner/english.all.3class.distsim.crf.ser.gz",
    "stanford_ner/stanford-ner.jar",
)

logf = logging.getLogger()


def parsedate_simple(s):
    if s == "":
        return ""

    return dateutil.parser.parse(s)


def traverse(scm, path):
    if "properties" in scm and type(scm["properties"]) == dict:
        return traverse(scm["properties"], path)

    if len(path) == 1:
        return scm.get(path[0], "")

    return traverse(scm.get(path[0], {}), path[1:])


def process_schema(mail):
    reservations = []
    for t in mail.text_html:
        schemas = extruct.extract(t)
        for scm in schemas["microdata"]:
            if scm["type"] == "http://schema.org/EmailMessage":
                pass
            elif scm["type"] == "http://schema.org/FlightReservation":
                reservations.append(
                    FlightEvent(
                        reservation_number=traverse(scm, ["reservationNumber"]),
                        flight_number=traverse(
                            scm, ["reservationFor", "airline", "iataCode"]
                        )
                        + traverse(scm, ["reservationFor", "flightNumber"]),
                        departure_airport_code=traverse(
                            scm, ["reservationFor", "departureAirport", "iataCode"]
                        ),
                        arrival_airport_code=traverse(
                            scm, ["reservationFor", "arrivalAirport", "iataCode"]
                        ),
                        departure_airport_name=traverse(
                            scm, ["reservationFor", "departureAirport", "name"]
                        ),
                        arrival_airport_name=traverse(
                            scm, ["reservationFor", "arrivalAirport", "name"]
                        ),
                        departure_time=parsedate_simple(
                            traverse(scm, ["reservationFor", "departureTime"])
                        ),
                        arrival_time=parsedate_simple(
                            traverse(scm, ["reservationFor", "arrivalTime"])
                        ),
                    )
                )
            else:
                reservations.append(
                    Notification(
                        "Unknown schema type, {}.  Is it interesting?".format(
                            scm.get("type", "NONE")
                        )
                    )
                )
        for scm in schemas["json-ld"]:
            if scm.get("@type", "") == "EmailMessage":
                pass
            elif scm.get("@type", "") == "LodgingReservation":
                reservations.append(
                    LodgingEvent(
                        reservation_number=traverse(scm, ["reservationNumber"]),
                        lodging_name=traverse(scm, ["reservationFor", "name"]),
                        lodging_address=traverse(
                            scm, ["reservationFor", "address", "streetAddress"]
                        ),
                        check_in=parsedate_simple(traverse(scm, ["checkinDate"])),
                        check_out=parsedate_simple(traverse(scm, ["checkoutDate"])),
                    )
                )
            elif scm.get("@type", "") == "FoodEstablishmentReservation":
                reservations.append(
                    RestaurantEvent(
                        reservation_number=traverse(scm, ["reservationNumber"]),
                        restaurant_name=traverse(scm, ["reservationFor", "name"]),
                        restaurant_address=traverse(
                            scm, ["reservationFor", "address", "streetAddress"]
                        ),
                        time=parsedate_simple(traverse(scm, ["startTime"])),
                        party=traverse(scm, ["partySize"]),
                    )
                )
            else:
                reservations.append(
                    Notification(
                        "Unknown schema type, {}.  Is it interesting?".format(
                            traverse(scm, "@type")
                        )
                    )
                )
    return reservations


def process_nlp(mail):
    def sanitize(txt):
        return txt.replace("\r", "").replace("\n\n", " .\n").replace("\n", " ")

    text = (
        " ".join(map(sanitize, mail.text_plain))
        or BeautifulSoup("".join(mail.text_html)).text
    )
    sentences = nltk.sent_tokenize(text)
    stemmer = nltk.PorterStemmer()
    time = None
    for sentence in sentences:
        # Ignore things that look like the next email in the list (and later)
        if "original" in sentence.lower() and "sent" in sentence.lower():
            break
        good = False
        for word in nltk.word_tokenize(sentence):
            stm = stemmer.stem(word)
            if stm in ["meet", "appoint", "see"]:
                good = True
                break
        # We pick the first response so as not to get things in the reply
        if good:
            time = dateparser.search.search_dates(
                sentence[:-1].replace(".", ":"),
                languages=["en"],
                settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": mail.date},
            )
            if time:
                time = time[0][1]

    if time is not None:
        is_personal = "robert" in text.lower() or "spencer" in text.lower()
        return [
            Appointment(
                summary="Meet with {}".format(mail.from_[0][0])
                if is_personal
                else mail.subject,
                start=time,
                location=None,
            )
        ]

    return []


def process_mail(mail):
    reservations = []
    if "schema.org" in mail.body:
        logf.info(
            'Parsing schema in email {} "{}"'.format(
                mail.date, mail.subject[:50] + (mail.subject[50:] and "...")
            )
        )
        reservations += process_schema(mail)
    reservations += process_nlp(mail)
    return reservations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logFormatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
    )
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    logging.getLogger().addHandler(consoleHandler)

    em = mailparser.parse_from_file(sys.argv[1])
    print(process_mail(em))
