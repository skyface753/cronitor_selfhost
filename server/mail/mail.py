import smtplib, ssl
import server.config.config as config
import os
import server.config.mail as mail_cnf
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(id, success, message, command):
    if config.MAIL_DISABLED:
        print("Email disabled => not sending email") if config.DEV else None
        return
    mailMessage = MIMEMultipart("alternative")
    mailMessage["Subject"] = "Cronitor Selfhost: " + id + " " + ("succeeded" if success else "failed")
    mailMessage["From"] = mail_cnf.SMTP_SENDER_EMAIL
    mailMessage["To"] = mail_cnf.SMTP_RECEIVER_EMAIL

    # Create the plain-text and HTML version of your message
    success = "succeeded" if success else "failed"
    text = """\
    Hi,
    Job {} {}.
    Command: {}
    Message: {}
    """.format(id, success, command, message)
    html = """\
    <html>
      <body>
        <p>Hi,<br>
              Job {} {}.<br>
                Command: {}<br>
                    Message: {}<br>
        </p>
      </body>
    </html>
    """.format(id, success, command, message)
    
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    mailMessage.attach(part1)
    mailMessage.attach(part2)
    
    print(mailMessage.as_string())
    
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(mail_cnf.SMTP_SERVER, mail_cnf.SMTP_PORT, context=context) as server:
        server.login(mail_cnf.SMTP_SENDER_EMAIL, mail_cnf.SMTP_PASSWORD)
        server.sendmail(mail_cnf.SMTP_SENDER_EMAIL, mail_cnf.SMTP_RECEIVER_EMAIL, mailMessage.as_string())
        if config.DEV:
            print("Email sent")
        
