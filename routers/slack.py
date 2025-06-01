from fastapi import APIRouter, Request, HTTPException
import json
import logging
from llm.utils import research_chain, reporter_chain
from slack.utils import verify_slack_signature
from slack.workflows import send_to_workflow

router = APIRouter(
    prefix="/v1"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/slack")
async def handle_slack(request: Request):
    """Single endpoint for all Slack requests"""
    try:
        # Get request data
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        
        # Read body
        body = await request.body()
        
        # Verify signature
        if not verify_slack_signature(body, timestamp, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except:
            # Handle form data (slash commands)
            form_data = {}
            for item in body.decode('utf-8').split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    form_data[key] = value.replace('+', ' ')
            payload = form_data
        
        # Handle URL verification
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}
        
        # Extract message text
        text = ""
        user = ""
        channel = ""
        
        if "event" in payload:  # Event API
            event = payload["event"]
            text = event.get("text", "")
            user = event.get("user", "")
            channel = event.get("channel", "")
        elif "text" in payload:  # Slash command
            text = payload.get("text", "")
            user = payload.get("user_id", "")
            channel = payload.get("channel_id", "")
        
        # Skip bot messages
        if payload.get("event", {}).get("subtype") == "bot_message":
            return {"status": "ignored"}
        
        # Process with AI if needed
        ai_response = ""
        if text:
            context = research_chain.invoke({"question": text})
            res = reporter_chain.invoke({"question": text, "context": context.content})
            ai_response = res.content
            logger.info(f"AI processed: {text[:50]}...")
        
        # Prepare workflow data
        workflow_data = {
            "user": user,
            "query": text,
            "message": text
        }
        
        # Add AI response to message if available
        if ai_response:
            workflow_data["message"] = f"{ai_response}"
        
        # Send to workflow
        send_to_workflow(workflow_data)
        
        return "Message sent 🚀"
        
    except Exception as e:
        print(e)
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server error")