from server.config.notify import NOTIFY_PROVIDER
from server.config.config import DEV
# Import the mail functions
from server.notifications.mail import mail_send_failed, mail_send_expired, mail_send_was_not_waiting, mail_send_resolved
# Import the discord functions
from server.notifications.discord import discord_send_failed, discord_send_expired, discord_send_was_not_waiting, discord_send_resolved


def send_failed(id, message, command):
    if NOTIFY_PROVIDER == None:
        print("No NOTIFY_PROVIDER set") if DEV else None
    elif NOTIFY_PROVIDER == "mail":
        mail_send_failed(id, message, command)
    elif NOTIFY_PROVIDER == "discord":
        discord_send_failed(id, message, command)
    
def send_expired(id):
    if NOTIFY_PROVIDER == None:
        print("No NOTIFY_PROVIDER set") if DEV else None
    elif NOTIFY_PROVIDER == "mail":
        mail_send_expired(id)
    elif NOTIFY_PROVIDER == "discord":
        discord_send_expired(id)
        
    
def send_was_not_waiting(id):
    if NOTIFY_PROVIDER == None:
        print("No NOTIFY_PROVIDER set") if DEV else None
    elif NOTIFY_PROVIDER == "mail":
        mail_send_was_not_waiting(id)
    elif NOTIFY_PROVIDER == "discord":
        discord_send_was_not_waiting(id)
        
def send_resolved(id):
    if NOTIFY_PROVIDER == None:
        print("No NOTIFY_PROVIDER set") if DEV else None
    elif NOTIFY_PROVIDER == "mail":
        mail_send_resolved(id)
    elif NOTIFY_PROVIDER == "discord":
        discord_send_resolved(id)