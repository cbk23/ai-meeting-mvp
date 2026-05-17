"""
Transcription Service
Handles audio transcription with multiple backends (Whisper, AssemblyAI)
"""

import os
import requests
import time
from typing import Optional
from pathlib import Path


class TranscriptionService:
    """Handle transcription with multiple backends (local or cloud)"""
    
    def __init__(self, backend: str = "local"):
        """
        Initialize transcription service
        
        Args:
            backend: 'local' (Whisper - free) or 'cloud' (AssemblyAI - paid)
        """
        self.backend = backend.lower()
        
        if self.backend == "cloud":
            self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "ASSEMBLYAI_API_KEY not set. "
                    "Get it from https://www.assemblyai.com"
                )
        
        print(f"Transcription service initialized with backend: {self.backend}")
    
    # ========== LOCAL TRANSCRIPTION (Whisper) ==========
    
    def transcribe_local(self, audio_file_path: str) -> str:
        """
        Transcribe using local Whisper model (free, offline)
        
        Models available: tiny, base (recommended), small, medium, large
        Base model is ~140MB download, provides good accuracy
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found: {audio_file_path}"
        
        try:
            import whisper
            
            print(f"Loading Whisper model (base)...")
            # Using 'base' model as good balance of speed/accuracy
            # Options: tiny, base, small, medium, large
            model = whisper.load_model("base")
            
            print(f"Transcribing audio: {audio_file_path}")
            result = model.transcribe(audio_file_path)
            
            transcription = result.get("text", "")
            
            if not transcription:
                return "Error: No speech detected in audio"
            
            print(f"Transcription complete: {len(transcription)} characters")
            return transcription
        
        except ImportError:
            return (
                "Error: Whisper not installed. "
                "Install with: pip install openai-whisper"
            )
        except Exception as e:
            return f"Transcription error: {str(e)}"
    
    # ========== CLOUD TRANSCRIPTION (AssemblyAI) ==========
    
    def transcribe_cloud(self, audio_file_path: str) -> str:
        """
        Transcribe using AssemblyAI (accurate, paid service)
        
        Cost: ~$0.10-0.50 per hour of audio
        Accuracy: Very high
        Speed: Fast
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found: {audio_file_path}"
        
        print(f"Uploading audio to AssemblyAI: {audio_file_path}")
        
        # Step 1: Upload file to AssemblyAI
        upload_url = "https://api.assemblyai.com/v2/upload"
        
        headers = {"Authorization": self.api_key}
        
        try:
            with open(audio_file_path, "rb") as f:
                upload_response = requests.post(
                    upload_url,
                    headers=headers,
                    data=f,
                    timeout=300  # 5 minute timeout for upload
                )
            
            if upload_response.status_code != 200:
                return f"Upload error: {upload_response.text}"
            
            audio_url = upload_response.json()["upload_url"]
            print(f"Audio uploaded: {audio_url}")
        
        except Exception as e:
            return f"Upload failed: {str(e)}"
        
        # Step 2: Submit transcription job
        print("Submitting transcription job...")
        
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        
        json_data = {
            "audio_url": audio_url,
            "language_code": "en",
            "speaker_labels": True  # Identify speakers
        }
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                transcript_url,
                json=json_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"Transcription submission error: {response.text}"
            
            transcript_id = response.json()["id"]
            print(f"Transcription job submitted: {transcript_id}")
        
        except Exception as e:
            return f"Transcription submission failed: {str(e)}"
        
        # Step 3: Poll for completion
        print("Waiting for transcription to complete...")
        
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        headers = {"Authorization": self.api_key}
        
        max_retries = 360  # 30 minutes with 5 second intervals
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(polling_endpoint, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    return f"Polling error: {response.text}"
                
                data = response.json()
                
                if data["status"] == "completed":
                    transcription = data.get("text", "")
                    print(f"Transcription complete: {len(transcription)} characters")
                    return transcription
                
                elif data["status"] == "error":
                    error_msg = data.get("error", "Unknown error")
                    return f"Transcription failed: {error_msg}"
                
                else:
                    # Still processing
                    progress = data.get("confidence", "unknown")
                    print(f"Status: {data['status']}... ({retry_count*5}s elapsed)")
                
                time.sleep(5)  # Check every 5 seconds
                retry_count += 1
            
            except Exception as e:
                return f"Polling failed: {str(e)}"
        
        return "Error: Transcription timeout (exceeded 30 minutes)"
    
    # ========== MAIN TRANSCRIPTION INTERFACE ==========
    
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using configured backend
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text or error message
        """
        
        if not os.path.exists(audio_file_path):
            return f"Error: File not found: {audio_file_path}"
        
        # Validate audio file
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        print(f"Audio file size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 1000:
            return f"Error: File too large ({file_size_mb:.2f} MB > 1000 MB limit)"
        
        print(f"Starting transcription with backend: {self.backend}")
        
        if self.backend == "local":
            return self.transcribe_local(audio_file_path)
        elif self.backend == "cloud":
            return self.transcribe_cloud(audio_file_path)
        else:
            return f"Error: Unknown backend: {self.backend}"
    
    # ========== UTILITY METHODS ==========
    
    def get_audio_duration(self, audio_file_path: str) -> Optional[float]:
        """Get duration of audio file in seconds"""
        
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(audio_file_path)
            duration_seconds = len(audio) / 1000.0
            
            return duration_seconds
        except ImportError:
            print("Warning: pydub not installed, cannot get duration")
            return None
        except Exception as e:
            print(f"Error getting duration: {str(e)}")
            return None
    
    def estimate_cost(self, audio_duration_seconds: float) -> dict:
        """Estimate transcription cost for AssemblyAI"""
        
        if self.backend != "cloud":
            return {"backend": self.backend, "cost": 0}
        
        # AssemblyAI pricing: ~$0.015 per minute
        cost_per_minute = 0.015
        minutes = audio_duration_seconds / 60
        estimated_cost = minutes * cost_per_minute
        
        return {
            "backend": "AssemblyAI",
            "duration_minutes": round(minutes, 2),
            "cost_per_minute": cost_per_minute,
            "estimated_cost": round(estimated_cost, 3)
        }


# For testing
if __name__ == "__main__":
    import sys
    
    backend = os.getenv("TRANSCRIPTION_BACKEND", "local")
    
    try:
        service = TranscriptionService(backend=backend)
        print(f"✅ Transcription service initialized with backend: {backend}")
    except Exception as e:
        print(f"❌ Failed to initialize service: {str(e)}")
        sys.exit(1)
    
    # Example usage:
    # result = service.transcribe("path/to/audio.mp3")
    # print(result)
