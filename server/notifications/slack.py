from slack_sdk import WebhookClient
import server.config.notify as notify
import server.config.config as config

def send_webhook(title, description, color):
    client = WebhookClient(notify.SLACK_WEBHOOK_URL)
    text = title + "\n" + description
    response = client.send(text=text, blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            },
            
        },
        {
            "type": "divider"
        }
    ])
    print(response) if config.DEV else None
    
def slack_send_failed(job_id, message, command):
    send_webhook(":x: Job failed: " + job_id, "Message: " + message + "\nCommand: " + command, "#ff0000")
    
def slack_send_expired(job_id):
    send_webhook(":x: Job expired: " + job_id, "Job was waiting and did not execute in time! Please check your jobs.json and your crontab!", "#ff0000")
    
def slack_send_was_not_waiting(job_id):
    send_webhook(":x: Job out of schedule: " + job_id, "Job was not waiting! Please check your jobs.json and your crontab!", "#ff0000")

def slack_send_resolved(job_id):
    send_webhook(":white_check_mark: Job resolved: " + job_id, "Job was resolved!", "#00ff00")