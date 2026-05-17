"""
Zoom Bot Service
Handles interaction with Zoom API to add bot to meetings and manage recordings
"""

import os
import requests
import json
import time
from typing import Optional, Dict
import jwt

class ZoomBotService:
    """Service to manage Zoom bot for meeting recording"""
    
    def __init__(self):
        self.client_id = os.getenv("ZOOM_CLIENT_ID")
        self.client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.bot_jid = os.getenv("ZOOM_BOT_JID")
        self.access_token = None
        self.token_expires_at = 0
        
        if not all([self.client_id, self.client_secret, self.bot_jid]):
            print("WARNING: Zoom credentials not fully configured")
    
    def get_access_token(self) -> str:
        """Get fresh Zoom API access token via JWT"""
        
        # Check if current token is still valid (with 5 min buffer)
        if self.access_token and time.time() < self.token_expires_at - 300:
            return self.access_token
        
        # Generate JWT token
        payload = {
            "iss": self.client_id,
            "exp": int(time.time()) + 3600
        }
        
        try:
            jwt_token = jwt.encode(
                payload,
                self.client_secret,
                algorithm="HS256"
            )
        except Exception as e:
            raise Exception(f"JWT encoding failed: {str(e)}")
        
        # Exchange JWT for access token
        url = "https://zoom.us/oauth/token"
        params = {
            "grant_type": "client_credentials",
            "assertion": jwt_token
        }
        
        try:
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data["expires_in"]
                return self.access_token
            else:
                raise Exception(f"Zoom auth failed: {response.text}")
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")
    
    def add_bot_to_meeting(self, meeting_id: str) -> Dict:
        """Add bot to a Zoom meeting to record it"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {str(e)}"
            }
        
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}/bot"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Bot join configuration
        payload = {
            "action": "start",
            "settings": {
                "bot_join_options": {
                    "join_option_parse_document_option": 1,
                    "leave_option_parse_document_option": 1
                }
            }
        }
        
        try:
            response = requests.patch(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return {
                    "status": "success",
                    "message": "Bot added to meeting",
                    "meeting_id": meeting_id
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": "Meeting not found",
                    "code": response.status_code
                }
            else:
                return {
                    "status": "error",
                    "message": response.text,
                    "code": response.status_code
                }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Request timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def remove_bot_from_meeting(self, meeting_id: str) -> Dict:
        """Remove bot from a Zoom meeting"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {str(e)}"
            }
        
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}/bot"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {"action": "stop"}
        
        try:
            response = requests.patch(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return {
                    "status": "success",
                    "message": "Bot removed from meeting"
                }
            else:
                return {
                    "status": "error",
                    "message": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_meeting_info(self, meeting_id: str) -> Dict:
        """Get details about a Zoom meeting"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}"}
        
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get meeting info: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_meeting_recordings(self, meeting_id: str) -> Dict:
        """Get recording files from a completed meeting"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}"}
        
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract recording files
                recording_files = []
                if "recording_files" in data:
                    for file in data["recording_files"]:
                        recording_files.append({
                            "id": file.get("id"),
                            "file_name": file.get("file_name"),
                            "file_type": file.get("file_type"),
                            "file_size": file.get("file_size"),
                            "download_url": file.get("download_url")
                        })
                
                return {
                    "status": "success",
                    "meeting_id": meeting_id,
                    "recordings": recording_files,
                    "total_size": data.get("total_size", 0)
                }
            else:
                return {"error": f"Failed to get recordings: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_user_recordings(self, user_id: str = "me") -> Dict:
        """Get all recordings for a user"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {"error": f"Authentication failed: {str(e)}"}
        
        url = f"https://api.zoom.us/v2/users/{user_id}/recordings"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get recordings: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    def download_recording(self, download_url: str, file_path: str) -> Dict:
        """Download a recording file"""
        
        try:
            token = self.get_access_token()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {str(e)}"
            }
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.get(
                download_url,
                headers=headers,
                timeout=300,  # 5 minute timeout for download
                stream=True
            )
            
            if response.status_code == 200:
                # Write to file
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return {
                    "status": "success",
                    "message": "Recording downloaded",
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Download failed: {response.text}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def is_configured(self) -> bool:
        """Check if Zoom credentials are properly configured"""
        
        return bool(
            self.client_id and
            self.client_secret and
            self.bot_jid
        )


# For testing
if __name__ == "__main__":
    service = ZoomBotService()
    
    if service.is_configured():
        print("✅ Zoom bot service is configured")
        
        # Test getting access token
        try:
            token = service.get_access_token()
            print(f"✅ Successfully obtained access token")
        except Exception as e:
            print(f"❌ Failed to get access token: {str(e)}")
    else:
        print("❌ Zoom credentials not configured")
        print("Please set ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_BOT_JID")
