import os
import server.config.config as config

SMTP_PORT = os.environ.get("SMTP_PORT") or 465  # For SSL
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") or None
SMTP_SENDER_EMAIL = os.environ.get("SMTP_SENDER_EMAIL") or None
SMTP_RECEIVER_EMAIL = os.environ.get("SMTP_RECEIVER_EMAIL") or None
SMTP_SERVER = os.environ.get("SMTP_SERVER") or None
if config.DEV:
    print("SMTP_PORT: " + str(SMTP_PORT))
    print("SMTP_PASSWORD: " + str(SMTP_PASSWORD))
    print("SMTP_SENDER_EMAIL: " + str(SMTP_SENDER_EMAIL))
    print("SMTP_RECEIVER_EMAIL: " + str(SMTP_RECEIVER_EMAIL))
    print("SMTP_SERVER: " + str(SMTP_SERVER))
    
if config.MAIL_DISABLED:
    print("Email disabled")
else:    
    if SMTP_PASSWORD is None or SMTP_SENDER_EMAIL is None or SMTP_RECEIVER_EMAIL is None or SMTP_SERVER is None:
        raise Exception("SMTP_PASSWORD, SMTP_SENDER_EMAIL, SMTP_RECEIVER_EMAIL or SMTP_SERVER not set")
    
