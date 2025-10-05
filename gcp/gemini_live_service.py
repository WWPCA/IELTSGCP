"""
Gemini 2.5 Flash Live API Service - Speech-to-Speech Conversations
Replaces AWS Bedrock Nova Sonic with Google Gemini Live API
"""
import asyncio
import json
import base64
import logging
import os
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime
import secrets

# Google Generative AI SDK
from google import genai
from google.genai.types import LiveConnectConfig, Modality, Blob
import librosa
import soundfile as sf
import io

logger = logging.getLogger(__name__)


class GeminiLiveService:
    """Service for Gemini 2.5 Flash Live API bidirectional speech-to-speech"""
    
    def __init__(self, project_id: Optional[str] = None, region: str = 'us-central1'):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.region = region
        
        # Configure for Vertex AI
        os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = self.region
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        
        # Initialize Gemini client
        self.client = genai.Client()
        
        # Model: gemini-2.5-flash-native-audio for best speech quality
        self.model_id = 'gemini-2.5-flash-native-audio-preview-09-2025'
        
        logger.info(f"Gemini Live client initialized - project: {self.project_id}, region: {self.region}")
    
    def get_maya_system_prompt(self, assessment_type: str = 'speaking') -> str:
        """Get system prompt for Maya IELTS examiner"""
        base_prompt = """You are Maya, a professional IELTS examiner conducting a speaking assessment.

Your role:
- Conduct the assessment following official IELTS speaking test format
- Ask clear questions appropriate to the test section
- Listen carefully and provide thoughtful follow-up questions
- Maintain professional, friendly demeanor
- Guide the conversation naturally

Assessment criteria you evaluate:
- Fluency and Coherence
- Lexical Resource (vocabulary)
- Grammatical Range and Accuracy
- Pronunciation

Remember: You are conducting an authentic IELTS speaking test. Be professional yet approachable."""
        
        if assessment_type == 'speaking_part1':
            return base_prompt + "\n\nThis is PART 1: Introduction and Interview (4-5 minutes). Ask about familiar topics like home, family, work, studies, interests."
        elif assessment_type == 'speaking_part2':
            return base_prompt + "\n\nThis is PART 2: Long Turn (3-4 minutes). Give a topic card and ask the candidate to speak for 1-2 minutes."
        elif assessment_type == 'speaking_part3':
            return base_prompt + "\n\nThis is PART 3: Two-way Discussion (4-5 minutes). Ask abstract questions related to Part 2 topic."
        
        return base_prompt
    
    async def start_maya_conversation(
        self,
        assessment_type: str = 'speaking',
        on_text_response: Optional[Callable[[str], None]] = None,
        on_audio_response: Optional[Callable[[bytes], None]] = None,
        content_moderation_callback: Optional[Callable[[str], bool]] = None
    ) -> 'GeminiLiveSession':
        """
        Start Maya conversation session with Gemini Live API
        
        Args:
            assessment_type: Type of IELTS assessment
            on_text_response: Callback for text transcripts
            on_audio_response: Callback for audio chunks
            content_moderation_callback: Check if content is appropriate
        
        Returns:
            GeminiLiveSession object for managing conversation
        """
        system_prompt = self.get_maya_system_prompt(assessment_type)
        
        config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=system_prompt
        )
        
        session = GeminiLiveSession(
            client=self.client,
            model_id=self.model_id,
            config=config,
            on_text_response=on_text_response,
            on_audio_response=on_audio_response,
            content_moderation_callback=content_moderation_callback
        )
        
        await session.connect()
        return session
    
    async def generate_assessment_feedback(
        self,
        transcript: str,
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        Generate detailed IELTS feedback using Gemini 2.5 Flash
        
        Args:
            transcript: Conversation transcript
            assessment_type: Type of assessment
        
        Returns:
            Structured feedback with scores and recommendations
        """
        feedback_prompt = f"""Analyze this IELTS {assessment_type} assessment transcript and provide detailed feedback.

Transcript:
{transcript}

Provide feedback in the following JSON format:
{{
    "overall_band": <float 0-9>,
    "fluency_coherence": {{
        "score": <float 0-9>,
        "strengths": [<list of strengths>],
        "areas_for_improvement": [<list of areas>]
    }},
    "lexical_resource": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "areas_for_improvement": [<list>]
    }},
    "grammatical_range": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "areas_for_improvement": [<list>]
    }},
    "pronunciation": {{
        "score": <float 0-9>,
        "strengths": [<list>],
        "areas_for_improvement": [<list>]
    }},
    "detailed_feedback": "<comprehensive paragraph>",
    "recommendations": [<list of actionable recommendations>]
}}"""
        
        try:
            # Use Gemini 2.5 Flash for text generation
            from google.genai import types
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=feedback_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            
            feedback = json.loads(response.text)
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to generate assessment feedback: {e}")
            raise


class GeminiLiveSession:
    """Manages an active Gemini Live API session"""
    
    def __init__(
        self,
        client: genai.Client,
        model_id: str,
        config: LiveConnectConfig,
        on_text_response: Optional[Callable] = None,
        on_audio_response: Optional[Callable] = None,
        content_moderation_callback: Optional[Callable] = None
    ):
        self.client = client
        self.model_id = model_id
        self.config = config
        self.session = None
        self.is_connected = False
        
        # Callbacks
        self.on_text_response = on_text_response
        self.on_audio_response = on_audio_response
        self.content_moderation_callback = content_moderation_callback
        
        # Session state
        self.conversation_transcript = []
        self.audio_buffer = []
        
        logger.info("GeminiLiveSession initialized")
    
    async def connect(self):
        """Connect to Gemini Live API"""
        try:
            self.session = await self.client.aio.live.connect(
                model=self.model_id,
                config=self.config
            ).__aenter__()
            
            self.is_connected = True
            logger.info("Connected to Gemini Live API")
            
            # Start response handler
            asyncio.create_task(self._handle_responses())
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Gemini Live API"""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.is_connected = False
            logger.info("Disconnected from Gemini Live API")
    
    async def send_audio(self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """
        Send audio input to Gemini
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM, 16kHz, mono)
            mime_type: Audio MIME type
        """
        if not self.is_connected:
            raise RuntimeError("Session not connected")
        
        try:
            # Convert audio to required format if needed
            audio_blob = Blob(
                data=audio_data,
                mime_type=mime_type
            )
            
            await self.session.send_realtime_input(audio=audio_blob)
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            raise
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """
        Send text input to Gemini
        
        Args:
            text: Text message
            end_of_turn: Whether this ends the user's turn
        """
        if not self.is_connected:
            raise RuntimeError("Session not connected")
        
        try:
            # Content moderation check
            if self.content_moderation_callback:
                if not self.content_moderation_callback(text):
                    logger.warning(f"Content moderation blocked text: {text[:50]}...")
                    return
            
            await self.session.send(text, end_of_turn=end_of_turn)
            self.conversation_transcript.append({
                'role': 'user',
                'content': text,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            raise
    
    async def _handle_responses(self):
        """Handle responses from Gemini (runs in background)"""
        try:
            async for message in self.session.receive():
                # Handle text response
                if message.text:
                    self.conversation_transcript.append({
                        'role': 'maya',
                        'content': message.text,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    
                    if self.on_text_response:
                        self.on_text_response(message.text)
                
                # Handle audio response
                if message.data:
                    # Audio is 16-bit PCM, 24kHz, mono
                    self.audio_buffer.append(message.data)
                    
                    if self.on_audio_response:
                        self.on_audio_response(message.data)
                
                # Check if turn is complete
                if message.server_content and message.server_content.turn_complete:
                    logger.debug("Turn complete")
                    
        except Exception as e:
            logger.error(f"Error handling responses: {e}")
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get conversation transcript"""
        return self.conversation_transcript
    
    def get_audio_recording(self) -> bytes:
        """Get complete audio recording"""
        return b''.join(self.audio_buffer)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Content Moderation Integration
class ContentModerationService:
    """Content moderation for Gemini Live conversations"""
    
    def __init__(self, project_id: str):
        # Use Google Cloud Natural Language API for content moderation
        from google.cloud import language_v1
        self.client = language_v1.LanguageServiceClient()
        self.project_id = project_id
    
    def check_content_safety(self, text: str) -> bool:
        """
        Check if content is safe for IELTS assessment
        
        Returns:
            True if content is safe, False otherwise
        """
        try:
            from google.cloud import language_v1
            
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            # Analyze sentiment and entities
            response = self.client.moderate_text(
                request={'document': document}
            )
            
            # Check moderation categories
            for category in response.moderation_categories:
                if category.confidence > 0.7:  # High confidence of inappropriate content
                    logger.warning(f"Content moderation triggered: {category.name}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Content moderation error: {e}")
            # Fail open - allow content if moderation fails
            return True
    
    def generate_warning_response(self, severity: str = 'mild') -> str:
        """Generate appropriate warning response for Maya"""
        if severity == 'mild':
            return "Let's keep our discussion focused on the IELTS assessment topics. Could you rephrase your response?"
        elif severity == 'moderate':
            return "I'm here to assess your English proficiency. Please ensure your responses relate to the assessment questions."
        else:  # severe
            return "I'm unable to continue this assessment due to inappropriate content. The session will now end."


# Utility functions
def convert_audio_to_pcm_16khz(audio_data: bytes, input_format: str = 'webm') -> bytes:
    """Convert audio to 16-bit PCM 16kHz format required by Gemini"""
    try:
        import io
        import librosa
        import soundfile as sf
        
        # Load audio
        buffer = io.BytesIO(audio_data)
        y, sr = librosa.load(buffer, sr=16000, mono=True)
        
        # Convert to PCM
        output_buffer = io.BytesIO()
        sf.write(output_buffer, y, sr, format='RAW', subtype='PCM_16')
        output_buffer.seek(0)
        
        return output_buffer.read()
        
    except Exception as e:
        logger.error(f"Audio conversion error: {e}")
        raise
