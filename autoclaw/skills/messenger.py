"""
AutoClaw - Autonomous AI Agent Platform
Messenger Skill

Sends messages via Feishu, Slack, Telegram, and Webhooks.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "messenger",
    "version": "1.0.0",
    "description": "Send messages via Feishu, Slack, Telegram, and Webhooks",
    "author": "AutoClaw Team",
    "capabilities": [
        "send_feishu",
        "send_slack",
        "send_telegram",
        "send_webhook",
        "receive_message"
    ]
}


class Messenger:
    """
    Messaging operations for multiple platforms.
    
    Features:
    - Send Feishu (Lark) messages
    - Send Slack messages
    - Send Telegram messages
    - Post to webhooks
    - Receive incoming messages
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.message_history = []
        
        # Platform configurations
        self.feishu_webhook = self.config.get("feishu_webhook", "")
        self.slack_webhook = self.config.get("slack_webhook", "")
        self.telegram_token = self.config.get("telegram_bot_token", "")
        self.telegram_chat_id = self.config.get("telegram_chat_id", "")
    
    async def send_feishu(self, message: str, webhook_url: Optional[str] = None,
                         msg_type: str = "text") -> Dict:
        """
        Send a message to Feishu (Lark).
        
        Args:
            message: Message content
            webhook_url: Feishu webhook URL (overrides config)
            msg_type: Message type (text, post, card)
            
        Returns:
            Send result
        """
        webhook = webhook_url or self.feishu_webhook
        
        if not webhook:
            return {
                "success": False,
                "error": "Feishu webhook URL not configured"
            }
        
        try:
            import aiohttp
            
            if msg_type == "text":
                payload = {
                    "msg_type": "text",
                    "content": {
                        "text": message
                    }
                }
            elif msg_type == "post":
                payload = {
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": "AutoClaw Notification",
                                "content": [[{"tag": "text", "text": message}]]
                            }
                        }
                    }
                }
            else:  # card
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "config": {"wide_screen_mode": True},
                        "elements": [{
                            "tag": "div",
                            "text": {"tag": "lark_md", "content": message}
                        }]
                    }
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook, json=payload) as response:
                    result = await response.json()
                    
                    self.message_history.append({
                        "platform": "feishu",
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "result": result
                    })
                    
                    return {
                        "success": True,
                        "platform": "feishu",
                        "message_id": result.get("data", {}).get("message_id", "unknown"),
                        "response": result
                    }
                    
        except ImportError:
            # Fallback without aiohttp
            return {
                "success": False,
                "error": "aiohttp not installed. Install with: pip install aiohttp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "feishu"
            }
    
    async def send_slack(self, message: str, webhook_url: Optional[str] = None,
                        channel: Optional[str] = None) -> Dict:
        """
        Send a message to Slack.
        
        Args:
            message: Message content
            webhook_url: Slack webhook URL (overrides config)
            channel: Target channel (overrides webhook default)
            
        Returns:
            Send result
        """
        webhook = webhook_url or self.slack_webhook
        
        if not webhook:
            return {
                "success": False,
                "error": "Slack webhook URL not configured"
            }
        
        try:
            import aiohttp
            
            payload = {
                "text": message,
                "username": "AutoClaw Bot",
                "icon_emoji": ":robot_face:"
            }
            
            if channel:
                payload["channel"] = channel
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook, json=payload) as response:
                    result_text = await response.text()
                    
                    self.message_history.append({
                        "platform": "slack",
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "channel": channel or "default"
                    })
                    
                    return {
                        "success": response.status == 200,
                        "platform": "slack",
                        "response": result_text
                    }
                    
        except ImportError:
            return {
                "success": False,
                "error": "aiohttp not installed. Install with: pip install aiohttp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "slack"
            }
    
    async def send_telegram(self, message: str, chat_id: Optional[str] = None,
                           parse_mode: str = "HTML") -> Dict:
        """
        Send a message to Telegram.
        
        Args:
            message: Message content (supports HTML/Markdown)
            chat_id: Target chat ID (overrides config)
            parse_mode: Parse mode (HTML, Markdown, MarkdownV2)
            
        Returns:
            Send result
        """
        token = self.telegram_token
        cid = chat_id or self.telegram_chat_id
        
        if not token:
            return {
                "success": False,
                "error": "Telegram bot token not configured"
            }
        
        if not cid:
            return {
                "success": False,
                "error": "Telegram chat ID not specified"
            }
        
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": cid,
                "text": message,
                "parse_mode": parse_mode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    
                    self.message_history.append({
                        "platform": "telegram",
                        "message": message,
                        "timestamp": datetime.now().isoformat(),
                        "chat_id": cid
                    })
                    
                    if result.get("ok"):
                        return {
                            "success": True,
                            "platform": "telegram",
                            "message_id": result["result"]["message_id"],
                            "chat_id": cid
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get("description", "Unknown error"),
                            "platform": "telegram"
                        }
                    
        except ImportError:
            return {
                "success": False,
                "error": "aiohttp not installed. Install with: pip install aiohttp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "telegram"
            }
    
    async def send_webhook(self, url: str, payload: Dict, 
                          method: str = "POST") -> Dict:
        """
        Send data to a custom webhook.
        
        Args:
            url: Webhook URL
            payload: Data to send
            method: HTTP method (POST, PUT, PATCH)
            
        Returns:
            Response from webhook
        """
        if not url:
            return {
                "success": False,
                "error": "Webhook URL not provided"
            }
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == "POST":
                    async with session.post(url, json=payload) as response:
                        result = await response.text()
                elif method.upper() == "PUT":
                    async with session.put(url, json=payload) as response:
                        result = await response.text()
                elif method.upper() == "PATCH":
                    async with session.patch(url, json=payload) as response:
                        result = await response.text()
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported method: {method}"
                    }
                
                self.message_history.append({
                    "platform": "webhook",
                    "url": url,
                    "method": method,
                    "timestamp": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "platform": "webhook",
                    "status_code": response.status,
                    "response": result
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "aiohttp not installed. Install with: pip install aiohttp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "webhook"
            }
    
    async def receive_message(self, platform: str, 
                             config_override: Optional[Dict] = None) -> Dict:
        """
        Receive messages from a platform (polling).
        
        Note: This is a simplified implementation. In production,
        you would use webhooks or long polling.
        
        Args:
            platform: Platform to receive from
            config_override: Override configuration
            
        Returns:
            Received messages
        """
        # This is a placeholder - real implementation would depend on platform
        return {
            "success": True,
            "platform": platform,
            "messages": [],
            "note": "Polling not implemented. Use webhooks for incoming messages."
        }
    
    def configure(self, platform: str, **kwargs):
        """Configure credentials for a platform."""
        if platform == "feishu":
            self.feishu_webhook = kwargs.get("webhook", self.feishu_webhook)
        elif platform == "slack":
            self.slack_webhook = kwargs.get("webhook", self.slack_webhook)
        elif platform == "telegram":
            self.telegram_token = kwargs.get("token", self.telegram_token)
            self.telegram_chat_id = kwargs.get("chat_id", self.telegram_chat_id)
        
        self.message_history.append({
            "type": "configuration",
            "platform": platform,
            "timestamp": datetime.now().isoformat()
        })
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method for tool manager compatibility."""
        if action == "send_feishu":
            return await self.send_feishu(
                kwargs.get("message", ""),
                kwargs.get("webhook_url"),
                kwargs.get("msg_type", "text")
            )
        elif action == "send_slack":
            return await self.send_slack(
                kwargs.get("message", ""),
                kwargs.get("webhook_url"),
                kwargs.get("channel")
            )
        elif action == "send_telegram":
            return await self.send_telegram(
                kwargs.get("message", ""),
                kwargs.get("chat_id"),
                kwargs.get("parse_mode", "HTML")
            )
        elif action == "send_webhook":
            return await self.send_webhook(
                kwargs.get("url", ""),
                kwargs.get("payload", {}),
                kwargs.get("method", "POST")
            )
        elif action == "receive_message":
            return await self.receive_message(
                kwargs.get("platform", ""),
                kwargs.get("config_override")
            )
        elif action == "configure":
            self.configure(kwargs.get("platform", ""), **kwargs.get("params", {}))
            return {"success": True, "message": "Configuration updated"}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
