import os
import logging
import requests
import json

SLACK_WORKFLOW_URL = os.getenv("SLACK_WORKFLOW_URL", "")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def send_to_workflow(data: dict) -> bool:
    """Send data to Slack workflow"""
    if not SLACK_WORKFLOW_URL:
        logger.info("No workflow URL configured")
        return False
    
    try:
        payload = json.dumps(data)
        headers = {
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Sending to workflow: {payload}")
        response = requests.post(SLACK_WORKFLOW_URL, headers=headers, data=payload, timeout=10)
        logger.info(f"Workflow response status: {response.status_code}")
        logger.info(f"Workflow response body: {response.text}")
        response.raise_for_status()
        logger.info("Sent to workflow successfully")
        return True
    except requests.exceptions.HTTPError as e:
        logger.error(f"Workflow HTTP error {response.status_code}: {response.text}")
        return False
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        return False