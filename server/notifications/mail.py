import smtplib, ssl
import server.config.config as config
import server.config.notify as mail_cnf
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def init_mailMessage(id, reason):
    mailMessage = MIMEMultipart("alternative")
    mailMessage["Subject"] = "Cronitor Selfhost: " + id + " " + reason
    mailMessage["From"] = mail_cnf.SMTP_FROM
    mailMessage["To"] = mail_cnf.SMTP_TO
    return mailMessage

def mail_send_failed(id, message, command):
    mailMessage = init_mailMessage(id, "failed")
    
    text = """\
    Job {} failed.
    Command: {}
    Message: {}
    """.format(id, command, message)
    html = """\
    <html>
      <body>
        <p>Job {} failed.<br>
            Command: {}<br>
            Message: {}<br>
        </p>
      </body>
    </html>
    """.format(id, command, message)
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    mailMessage.attach(part1)
    mailMessage.attach(part2)
    
    send_email(mailMessage)
    
def mail_send_expired(id):
    mailMessage = init_mailMessage(id, "expired")
    
    text = """\
    Job {} expired.
    Please check your crontab.
    """.format(id)
    html = """\
    <html>
      <body>
        <p>Job {} expired.<br>
            Please check your crontab.<br>
        </p>
      </body>
    </html>
    """.format(id)
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    mailMessage.attach(part1)
    mailMessage.attach(part2)
    
    send_email(mailMessage)

def mail_send_was_not_waiting(id):
    mailMessage = init_mailMessage(id, "was not waiting")
    
    text = """\
    Job {} was not waiting.
    Please check your crontab and the jobs.json file.
    """.format(id)
    html = """\
    <html>
      <body>
        <p>Job {} was not waiting.<br>
            Please check your crontab and the jobs.json file.<br>
        </p>
      </body>
    </html>
    """.format(id)
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    mailMessage.attach(part1)
    mailMessage.attach(part2)
    
    send_email(mailMessage)
        
def mail_send_resolved(id):
    mailMessage = init_mailMessage(id, "resolved")
    
    text = """\
    Job {} resolved.
    """.format(id)
    html = """\
    <html>
      <body>
        <p>Job {} resolved.<br>
        </p>
      </body>
    </html>
    """.format(id)
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    
    mailMessage.attach(part1)
    mailMessage.attach(part2)
    
    send_email(mailMessage)

def send_email(mailMessage):
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(mail_cnf.SMTP_HOST, mail_cnf.SMTP_PORT, context=context) as server:
        server.login(mail_cnf.SMTP_USERNAME, mail_cnf.SMTP_PASSWORD)
        server.sendmail(mail_cnf.SMTP_FROM, mail_cnf.SMTP_TO, mailMessage.as_string())
        print("Email sent") if config.DEV else None
        
