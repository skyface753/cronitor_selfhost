import os
import server.config.config as config

NOTIFY_DISCORD = False 
NOTIFY_MAIL = False

if os.environ.get("NOTIFY_DISCORD") is not None:
    if os.environ.get("NOTIFY_DISCORD").lower() == "true" or os.environ.get("NOTIFY_DISCORD") == "1":
        NOTIFY_DISCORD = True
if os.environ.get("NOTIFY_MAIL") is not None:
    if os.environ.get("NOTIFY_MAIL").lower() == "true" or os.environ.get("NOTIFY_MAIL") == "1":
        NOTIFY_MAIL = True
if config.DEV:
    print("NOTIFY_DISCORD: " + str(NOTIFY_DISCORD))
    print("NOTIFY_MAIL: " + str(NOTIFY_MAIL))

SMTP_PORT = os.environ.get("SMTP_PORT") or 465  # For SSL
SMTP_USERNAME = os.environ.get("SMTP_USERNAME") or None
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") or None
SMTP_FROM = os.environ.get("SMTP_FROM") or None
SMTP_TO = os.environ.get("SMTP_TO") or None
SMTP_HOST = os.environ.get("SMTP_HOST") or None
if config.DEV:
    print("SMTP_PORT: " + str(SMTP_PORT))
    print("SMTP_USERNAME: " + str(SMTP_USERNAME))
    print("SMTP_PASSWORD: " + "********" if SMTP_PASSWORD is not None else "None")
    print("SMTP_FROM: " + str(SMTP_FROM))
    print("SMTP_TO: " + str(SMTP_TO))
    print("SMTP_HOST: " + str(SMTP_HOST))


if NOTIFY_DISCORD is False and NOTIFY_MAIL is False:
    print("------ NO NOTIFY PROVIDER ENABELD! -------")
    print("------ You will not receive any notifications! -------")


DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL") or None
if config.DEV:
    print("DISCORD_WEBHOOK_URL: " + str(DISCORD_WEBHOOK_URL))
if NOTIFY_DISCORD:
    if DISCORD_WEBHOOK_URL is None:
        raise Exception("DISCORD_WEBHOOK_URL not set")
if NOTIFY_MAIL:
    if SMTP_PASSWORD is None or SMTP_FROM is None or SMTP_TO is None or SMTP_HOST is None or SMTP_USERNAME is None:
        raise Exception("SMTP_PASSWORD, SMTP_FROM, SMTP_TO, SMTP_HOST or SMTP_USERNAME not set")
    


    


