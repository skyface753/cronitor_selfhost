import os
import server.config.config as config

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
    
if config.MAIL_DISABLED:
    print("Email disabled")
else:    
    if SMTP_PASSWORD is None or SMTP_FROM is None or SMTP_TO is None or SMTP_HOST is None or SMTP_USERNAME is None:
        raise Exception("SMTP_PASSWORD, SMTP_FROM, SMTP_TO, SMTP_HOST or SMTP_USERNAME not set")
    
