# TTS toolkit - LangChain wrapper for text-to-speech tools
from langchain.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field
from tools.tts import tts_manager

class GenerateSpeechInput(BaseModel):
    """Input for generate_speech tool"""
    text: str = Field(description="Text to convert to speech")
    voice_id: Optional[str] = Field(None, description="ElevenLabs voice ID (optional, uses default if not specified)")

class GenerateSpeechTool(BaseTool):
    name: str = "generate_speech"
    description: str = """Generate speech audio from text using ElevenLabs.
    Returns file_id that can be used to access the audio file.

    Args:
        text: The text to convert to speech
        voice_id: (optional) ElevenLabs voice ID to use

    Returns:
        Dict with file_id, filename, size_bytes
    """
    args_schema: type[BaseModel] = GenerateSpeechInput

    def _run(self, text: str, voice_id: Optional[str] = None) -> str:
        """Generate speech and return file info"""
        try:
            result = tts_manager.generate_speech(
                text=text,
                user_id="default",  # TODO: get from context
                voice_id=voice_id
            )
            return f"Generated speech file_id={result['file_id']}, filename={result['filename']}, size={result['size_bytes']} bytes"
        except Exception as e:
            return f"Error generating speech: {str(e)}"

class ListVoicesInput(BaseModel):
    """Input for list_voices tool"""
    pass

class ListVoicesTool(BaseTool):
    name: str = "list_voices"
    description: str = """List available ElevenLabs voices.

    Returns:
        List of available voices with their IDs and names
    """
    args_schema: type[BaseModel] = ListVoicesInput

    def _run(self) -> str:
        """List available voices"""
        try:
            voices = tts_manager.list_voices()
            voice_list = "\n".join([
                f"- {v['name']} (ID: {v['voice_id']})" + (f" [{v['category']}]" if v['category'] else "")
                for v in voices[:10]  # Limit to first 10 to avoid token bloat
            ])
            return f"Available voices:\n{voice_list}"
        except Exception as e:
            return f"Error listing voices: {str(e)}"

class TTSToolkit:
    """Toolkit for text-to-speech operations"""

    def get_tools(self):
        """Get list of TTS tools"""
        return [
            GenerateSpeechTool(),
            ListVoicesTool()
        ]
