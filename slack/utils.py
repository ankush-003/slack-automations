import os
import hmac
import hashlib

# Configuration
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

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