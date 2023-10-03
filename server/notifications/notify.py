from server.config.notify import NOTIFY_PROVIDER
from server.config.config import DEV
# Import the mail functions
from server.notifications.mail import mail_send_failed, mail_send_expired, mail_send_was_not_waiting, mail_send_resolved
# Import the discord functions
from server.notifications.discord import discord_send_failed, discord_send_expired, discord_send_was_not_waiting, discord_send_resolved

# type: "expired", "failed", "was_not_waiting", "resolved"
def send_notification(id, type= None, message=None, command=None):
    if type == None:
        raise Exception("Notification type not set!")
    if NOTIFY_PROVIDER is None:
        print("No NOTIFY_PROVIDER set") if DEV else None
    elif NOTIFY_PROVIDER == "mail":
        if type == "expired":
            mail_send_expired(id)
        elif type == "failed":
            mail_send_failed(id, message, command)
        elif type == "was_not_waiting":
            mail_send_was_not_waiting(id)
        elif type == "resolved":
            mail_send_resolved(id)
    elif NOTIFY_PROVIDER == "discord":
        if type == "expired":
            discord_send_expired(id)
        elif type == "failed":
            discord_send_failed(id, message, command)
        elif type == "was_not_waiting":
            discord_send_was_not_waiting(id)
        elif type == "resolved":
            discord_send_resolved(id)
    else:
        print(f"Invalid NOTIFY_PROVIDER: {NOTIFY_PROVIDER}") if DEV else None
        raise Exception("Invalid NOTIFY_PROVIDER")

