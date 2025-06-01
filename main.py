from fastapi import FastAPI
import logging
# from slack_bolt import App
import os
from routers import slack

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# app = App(
#     token=os.environ.get("SLACK_BOT_TOKEN"),
#     signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
# )

# Listens to incoming messages that contain "hello"
# @app.message("hello")
# def message_hello(message, say):
#     # say() sends a message to the channel where the event was triggered
#     say(f"Hey there <@{message['user']}>!")

app = FastAPI(title="Slack Bot API", version="1.0.0")

# Include routers
app.include_router(slack.router)

@app.get("/")
def health_check():
    """Health check"""
    return {"status": "healthy"}