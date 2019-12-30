"""Functionality relating to emails."""

import datetime
import imaplib
import logging

import mailparser

import talon
import talon.signature
from talon.signature.bruteforce import extract_signature

import yaml

config = yaml.full_load(open("config.yaml"))

talon.init()

logger = logging.getLogger(__name__)


def get_receiving_mailboxes(imap_connection):
    """Find all "receiving" mailboxes associated to the account.

    Skips sent items, deleted items and trash.
    """
    r, mailboxes = imap_connection.list()
    if r != "OK":
        logger.error("Cannot list mailboxes")
        return []
    mailboxes = [mb.decode("utf-8").split(' "/" ')[1] for mb in mailboxes]
    return [
        mailbox
        for mailbox in mailboxes
        if mailbox.lower() not in {"spam", "trash", "deleted", "sent"}
    ]


def get_emails_since(when: datetime.datetime, inbox_only: bool = False):
    """Get a list of emails from all accounts for the user sent after a certain time."""
    logger.info("Fetching emails since %s", when)
    emails = []
    for email_account in config["email_accounts"]:
        logger.info("Opening email account %s", email_account["name"])
        with imaplib.IMAP4_SSL(email_account["server"]) as imap_connection:
            imap_connection.login(email_account["username"], email_account["password"])
            if inbox_only:
                mailboxes = ["INBOX"]
            else:
                mailboxes = get_receiving_mailboxes(imap_connection)
            for mailbox in mailboxes:
                logger.info("Checking mailbox %s", mailbox)
                resp, _ = imap_connection.select(mailbox, readonly=True)
                if resp != "OK":
                    logger.warn(
                        "Could not select mailbox %s in account %s",
                        mailbox,
                        email_account["name"],
                    )
                    continue
                r, data = imap_connection.search(
                    None, '(SINCE "{}")'.format(when.strftime("%d-%b-%Y"))
                )
                for message_uid in data[0].decode("utf-8").split():
                    r, data = imap_connection.fetch(message_uid, "(RFC822)")
                    try:
                        email = mailparser.parse_from_bytes(data[0][1])
                        email.uid = "{}/{}/{}".format(
                            email_account["name"], mailbox, message_uid
                        )
                        if email.date >= when:
                            emails.append(email)
                    except Exception as e:
                        continue
    return emails


def extract_message(mail: mailparser.MailParser) -> str:
    """Extract the message from the email as a human would read it."""
    for part in mail.text_plain:
        return talon.quotations.extract_from_plain(part)
    for part in mail.text_html:
        return talon.quotations.extract_from_html(part)


def extract_salutation(mail: mailparser.MailParser) -> str:
    """Extract the salutation from the email as a human would read it."""
    result = extract_signature(extract_message(mail))[1]
    if result is None:
        result = talon.signature.extract(extract_message(mail), mail.from_[0][1])[1]
    return result
