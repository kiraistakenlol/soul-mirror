# Text-to-speech tool using ElevenLabs API
import os
from typing import Optional, Dict
from dotenv import load_dotenv
from repository.files import FilesRepository

load_dotenv()

class TTSManager:
    """Manages text-to-speech generation using ElevenLabs"""

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        self.files_repo = FilesRepository()

    def generate_speech(self, text: str, user_id: str = "default",
                       voice_id: Optional[str] = None,
                       model_id: str = "eleven_monolingual_v1") -> Dict:
        """
        Generate speech from text using ElevenLabs API

        Args:
            text: Text to convert to speech
            user_id: User identifier for file storage
            voice_id: ElevenLabs voice ID (uses default if not specified)
            model_id: ElevenLabs model ID

        Returns:
            Dict with file_id, filename, size_bytes, metadata
        """
        from elevenlabs import VoiceSettings
        from elevenlabs.client import ElevenLabs

        # Use default voice if not specified (Rachel - clear, expressive)
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"

        client = ElevenLabs(api_key=self.api_key)

        # Generate speech
        print(f"🔊 Generating speech for text: {text[:50]}...")
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=model_id,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True
            )
        )

        # Collect audio bytes
        audio_bytes = b"".join(audio_generator)
        print(f"✓ Generated {len(audio_bytes)} bytes of audio")

        # Prepare metadata
        metadata = {
            "voice_id": voice_id,
            "model_id": model_id,
            "text_length": len(text),
            "text_preview": text[:100]
        }

        # Store in database
        filename = f"speech_{text[:30].replace(' ', '_')}.mp3"
        file_id = self.files_repo.create_file(
            user_id=user_id,
            filename=filename,
            file_type="voiceover",
            content_type="audio/mpeg",
            data=audio_bytes,
            metadata=metadata
        )

        print(f"✓ Saved audio as file_id={file_id}")

        return {
            "file_id": file_id,
            "filename": filename,
            "size_bytes": len(audio_bytes),
            "metadata": metadata
        }

    def list_voices(self) -> list:
        """List available ElevenLabs voices"""
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=self.api_key)
        voices = client.voices.get_all()

        return [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category if hasattr(voice, 'category') else None
            }
            for voice in voices.voices
        ]


# Global instance
tts_manager = TTSManager()
