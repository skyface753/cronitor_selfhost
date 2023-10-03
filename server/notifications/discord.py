from discord_webhook import DiscordWebhook, DiscordEmbed
import server.config.notify as notify
import server.config.config as config
import datetime

def send_webhook(title, description, color):
    webhook = DiscordWebhook(url=notify.DISCORD_WEBHOOK_URL)
    embed = DiscordEmbed(title=title, description=description, color=color)
    webhook.add_embed(embed)
    response = webhook.execute()
    print(response) if config.DEV else None

def discord_send_failed(job_id, message, command):
    send_webhook(":x: Job failed: " + job_id, "Message: " + message + "\nCommand: " + command, 16711680)
    
def discord_send_expired(job_id):
    send_webhook(":x: Job expired: " + job_id, "Job was waiting and did not execute in time! Please check your jobs.json and your crontab!", 16711680)
    
def discord_send_was_not_waiting(job_id):
    send_webhook(":x: Job out of schedule: " + job_id, "Job was not waiting! Please check your jobs.json and your crontab!", 16711680)
    
def discord_send_resolved(job_id):
    send_webhook(":white_check_mark: Job resolved: " + job_id, "Job was resolved!", 65280)

