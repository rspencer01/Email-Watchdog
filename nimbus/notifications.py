"""Procedures for push interactions with users.

At the moment all push notifications are through telegram.
"""
import datetime

import telegram

import yaml

from .persistent.notification import Notification

config = yaml.full_load(open("config.yaml"))

bot = telegram.Bot(token=config["telegram"]["token"])


def query_menu(notification_id) -> str:
    """Construct a telegram query menu for a notification with response requested."""
    return [
        [
            telegram.InlineKeyboardButton(
                text="Yes", callback_data="{}|yes".format(notification_id)
            )
        ],
        [
            telegram.InlineKeyboardButton(
                text="No", callback_data="{}|no".format(notification_id)
            )
        ],
    ]


EMPTY_MENU = [[]]


def add_notification(message: str, response_required: bool = False) -> int:
    """Add a notification to the queue."""
    notification = Notification.create(
        message=message,
        response_required=response_required,
        created=datetime.datetime.now(),
    )
    notification.save()
    return notification.id


def are_unanswered_posed_notifications():
    """Check if we are waiting on a response to a notification."""
    unanswered_posed_notifications = Notification.select().where(
        (Notification.posed == True)
        & (Notification.response_required == True)
        & (Notification.response.is_null())
        & (Notification.created >= datetime.datetime.now() - datetime.timedelta(days=1))
    )
    return unanswered_posed_notifications.exists()


def mark_response(response_data: str) -> None:
    """Parse the response data and update the notification."""
    updated_notification = Notification[int(response_data.split("|")[0])]
    updated_notification.response = response_data.split("|")[1]
    updated_notification.save()
    return updated_notification


def check_for_responses():
    """Check the telegram queue for any responses to notifications.

    Returns true if some message was responded to.
    """
    if are_unanswered_posed_notifications():
        try:
            updates = bot.getUpdates(timeout=1, allowed_updates=["callback_query"])
        except telegram.error.TimedOut:
            return False
        for update in updates:
            try:
                updated_notification = mark_response(update.callback_query.data)
                bot.answerCallbackQuery(update.callback_query.id)
                bot.editMessageReplyMarkup(
                    chat_id=config["telegram"]["chat_id"],
                    message_id=updated_notification.telegram_id,
                    reply_markup=telegram.InlineKeyboardMarkup([[]]),
                )
            except telegram.utils.request.BadRequest:
                continue
        if updates != []:
            bot.getUpdates(
                offset=int(updates[-1].callback_query.id) + 1,
                timeout=1,
                allowed_updates=["callback_query"],
            )
    return True


def send_new_notifications() -> None:
    """Send one new notification, if it exists."""
    unposed_notifications = (
        Notification.select()
        .where(Notification.posed == False)
        .order_by(Notification.created)
    )
    if unposed_notifications.exists():
        notification = unposed_notifications.get()
        menu = (
            query_menu(notification.id)
            if notification.response_required
            else EMPTY_MENU
        )
        reply_markup = telegram.InlineKeyboardMarkup(menu)
        notification.telegram_id = bot.sendMessage(
            chat_id=config["telegram"]["chat_id"],
            text=notification.message,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.MARKDOWN,
        ).message_id
        notification.posed = True
        notification.save()


def update() -> None:
    """Check on the user.

    First check if there is a response to any notification, and then send any new ones.
    """
    check_for_responses()
    send_new_notifications()


def get_response(notification_id: int) -> list:
    """Get a response to a notification."""
    return Notification[notification_id].response
