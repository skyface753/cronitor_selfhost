from server.config.notify import NOTIFY_DISCORD, NOTIFY_MAIL, NOTIFY_SLACK
from server.config.config import DEV
# Import the mail functions
from server.notifications.mail import mail_send_failed, mail_send_expired, mail_send_was_not_waiting, mail_send_resolved
# Import the discord functions
from server.notifications.discord import discord_send_failed, discord_send_expired, discord_send_was_not_waiting, discord_send_resolved
# Import the slack functions
from server.notifications.slack import slack_send_failed, slack_send_expired, slack_send_was_not_waiting, slack_send_resolved

# type: "expired", "failed", "was_not_waiting", "resolved"
def send_notification(id, type= None, message=None, command=None):
    if type == None:
        raise Exception("Notification type not set!")
    if NOTIFY_DISCORD is None and NOTIFY_MAIL is None:
        print("No notify provider enabled!") 
        return
    if NOTIFY_MAIL is not None:
        if type == "expired":
            mail_send_expired(id)
        elif type == "failed":
            mail_send_failed(id, message, command)
        elif type == "was_not_waiting":
            mail_send_was_not_waiting(id)
        elif type == "resolved":
            mail_send_resolved(id)
    if NOTIFY_DISCORD is not None:
        if type == "expired":
            discord_send_expired(id)
        elif type == "failed":
            discord_send_failed(id, message, command)
        elif type == "was_not_waiting":
            discord_send_was_not_waiting(id)
        elif type == "resolved":
            discord_send_resolved(id)
    if NOTIFY_SLACK is not None:
        if type == "expired":
            slack_send_expired(id)
        elif type == "failed":
            slack_send_failed(id, message, command)
        elif type == "was_not_waiting":
            slack_send_was_not_waiting(id)
        elif type == "resolved":
            slack_send_resolved(id)
        
