from fastapi import FastAPI, Request, HTTPException
import httpx
import hashlib
import hmac
import time
import json
import os
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Slack Bot API", version="1.0.0")

# Configuration
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
SLACK_WORKFLOW_URL = os.getenv("SLACK_WORKFLOW_URL", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Configure Google AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Verify Slack signature"""
    if not SLACK_SIGNING_SECRET:
        return True  # Skip verification if no secret configured
    
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    expected_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

def should_process_with_ai(text: str) -> bool:
    """Check if message should use AI"""
    text = text.lower()
    return "help" in text or "?" in text or text.startswith("ai")

def get_ai_response(text: str) -> str:
    """Get AI response"""
    if not model:
        return "AI not configured"
    
    try:
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "AI error occurred"

def send_to_workflow(data: dict) -> bool:
    """Send data to Slack workflow"""
    if not SLACK_WORKFLOW_URL:
        logger.info("No workflow URL configured")
        return False
    
    try:
        response = httpx.post(SLACK_WORKFLOW_URL, json=data, timeout=10)
        response.raise_for_status()
        logger.info("Sent to workflow successfully")
        return True
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return False

@app.post("/slack")
def handle_slack(request: Request):
    """Single endpoint for all Slack requests"""
    try:
        # Get request data
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")
        
        # Read body synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        body = loop.run_until_complete(request.body())
        
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
            user = payload.get("user_name", "")
            channel = payload.get("channel_id", "")
        
        # Skip bot messages
        if payload.get("event", {}).get("subtype") == "bot_message":
            return {"status": "ignored"}
        
        # Process with AI if needed
        ai_response = ""
        if text and should_process_with_ai(text):
            ai_response = get_ai_response(text)
            logger.info(f"AI processed: {text[:50]}...")
        
        # Prepare workflow data
        workflow_data = {
            "message": text,
            "user": user,
            "channel": channel,
            "ai_response": ai_response,
            "timestamp": time.time()
        }
        
        # Send to workflow
        send_to_workflow(workflow_data)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/")
def health_check():
    """Health check"""
    return {"status": "healthy", "ai_enabled": model is not None}