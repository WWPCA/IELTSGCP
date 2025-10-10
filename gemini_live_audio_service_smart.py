"""
Gemini 2.5 Flash Live API Service with Smart Selection
Optimized for IELTS with dynamic model switching
Cost: ~$0.025 per 14-minute session (vs $0.059 for all Flash)
"""
import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import secrets

# Google Generative AI SDK
from google import genai
from google.genai.types import LiveConnectConfig, Modality, Blob

# Import workflow manager for Smart Selection
from ielts_workflow_manager import IELTSWorkflowManager, SmartSelectionOrchestrator

logger = logging.getLogger(__name__)


class GeminiLiveServiceSmart:
    """
    Enhanced Gemini Live service with Smart Selection support
    Automatically optimizes model usage based on IELTS part and complexity
    """
    
    def __init__(self, project_id: Optional[str] = None, region: str = 'us-central1'):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.region = region
        
        # Configure for Vertex AI
        os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = self.region
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        
        # Initialize Gemini client
        self.client = genai.Client()
        
        # Smart Selection models
        self.models = {
            'flash-lite': 'gemini-2.5-flash-lite',
            'flash': 'gemini-2.5-flash',
            'flash-native': 'gemini-2.5-flash-native-audio-preview-09-2025'
        }
        
        # Do NOT create shared workflow manager - each session needs its own!
        
        logger.info(f"Gemini Live Smart Selection initialized - project: {self.project_id}")
    
    async def start_maya_conversation_smart(
        self,
        assessment_type: str = 'speaking',
        on_text_response: Optional[Callable[[str], None]] = None,
        on_audio_response: Optional[Callable[[bytes], None]] = None,
        content_moderation_callback: Optional[Callable[[str], bool]] = None
    ) -> 'GeminiLiveSessionSmart':
        """
        Start Maya conversation with Smart Selection optimization
        
        Args:
            assessment_type: Type of IELTS assessment
            on_text_response: Callback for text transcripts
            on_audio_response: Callback for audio chunks
            content_moderation_callback: Check if content is appropriate
        
        Returns:
            GeminiLiveSessionSmart object with workflow management
        """
        # Create a NEW workflow manager for THIS session (not shared!)
        workflow_manager = IELTSWorkflowManager()
        
        # Start with Part 1 configuration
        config = workflow_manager.update_state_for_part(1)
        
        # Create Live config with optimized prompt
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=config['prompt']
        )
        
        # Create Smart session with its own workflow manager
        session = GeminiLiveSessionSmart(
            client=self.client,
            model_id=config['model'],
            config=live_config,
            workflow_manager=workflow_manager,  # Pass the NEW instance
            on_text_response=on_text_response,
            on_audio_response=on_audio_response,
            content_moderation_callback=content_moderation_callback
        )
        
        await session.connect()
        logger.info(f"Started Smart Selection conversation - Part 1 with {config['model']}")
        
        return session


class GeminiLiveSessionSmart:
    """
    Enhanced Gemini Live session with Smart Selection workflow
    Manages dynamic model switching and structured evaluation
    """
    
    def __init__(
        self,
        client: genai.Client,
        model_id: str,
        config: LiveConnectConfig,
        workflow_manager: IELTSWorkflowManager,
        on_text_response: Optional[Callable] = None,
        on_audio_response: Optional[Callable] = None,
        content_moderation_callback: Optional[Callable] = None
    ):
        self.client = client
        self.model_id = model_id
        self.config = config
        self.workflow_manager = workflow_manager
        self.on_text_response = on_text_response
        self.on_audio_response = on_audio_response
        self.content_moderation_callback = content_moderation_callback
        
        self.session = None
        self.is_connected = False
        self.conversation_transcript = []
        self.audio_buffer = []
        self.response_task = None
        
        # Track messages for part transitions
        self.messages_in_current_part = 0
    
    async def connect(self):
        """Establish connection with Gemini Live API"""
        try:
            # Create session with current model
            self.session = await self.client.models.generate_content_stream(
                model=self.model_id,
                config=self.config
            )
            self.is_connected = True
            
            # Start response handler
            self.response_task = asyncio.create_task(self._handle_responses())
            
            logger.info(f"Connected to Gemini Live API with model {self.model_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            raise
    
    async def switch_model(self, new_model: str, new_prompt: str):
        """
        Switch to a different model mid-conversation
        Used when transitioning between parts or complexity detected
        """
        if not self.is_connected:
            logger.warning("Cannot switch model - not connected")
            return
        
        try:
            logger.info(f"Switching model from {self.model_id} to {new_model}")
            
            # Update config with new prompt
            self.config.system_instruction = new_prompt
            
            # Close current session
            if self.session:
                await self.session.close()
            
            # Create new session with new model
            self.model_id = new_model
            self.session = await self.client.models.generate_content_stream(
                model=self.model_id,
                config=self.config
            )
            
            # Reset message counter for new part
            self.messages_in_current_part = 0
            
            logger.info(f"Successfully switched to {new_model}")
            
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            raise
    
    async def check_and_transition_parts(self):
        """
        Check if it's time to transition to next IELTS part
        Automatically switches model and prompt as needed
        """
        if self.workflow_manager.should_transition():
            next_part = self.workflow_manager.state.current_part + 1
            
            if next_part <= 3:
                # Get configuration for next part
                config = self.workflow_manager.update_state_for_part(next_part)
                
                # Switch model and prompt
                await self.switch_model(config['model'], config['prompt'])
                
                logger.info(f"Transitioned to Part {next_part} with {config['model']}")
                
                # Notify about transition
                if self.on_text_response:
                    transition_msg = f"[Transitioning to Part {next_part}]"
                    self.on_text_response(transition_msg)
                
                return True
        
        return False
    
    async def send_audio(self, audio_data: bytes, mime_type: str = 'audio/wav'):
        """
        Send audio input to Gemini with automatic part tracking
        
        Args:
            audio_data: Audio bytes
            mime_type: Audio MIME type
        """
        if not self.is_connected:
            raise RuntimeError("Session not connected")
        
        try:
            # Track response for workflow
            self.workflow_manager.track_response('candidate', f"[Audio input {len(audio_data)} bytes]")
            self.messages_in_current_part += 1
            
            # Convert audio to required format if needed
            audio_blob = Blob(
                data=audio_data,
                mime_type=mime_type
            )
            
            await self.session.send_realtime_input(audio=audio_blob)
            
            # Check if we should transition parts
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            raise
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """
        Send text input to Gemini with automatic part tracking
        
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
            
            # Track response for workflow
            self.workflow_manager.track_response('candidate', text)
            self.messages_in_current_part += 1
            
            # Add to transcript
            self.conversation_transcript.append({
                'role': 'candidate',
                'content': text,
                'timestamp': datetime.utcnow().isoformat(),
                'part': self.workflow_manager.state.current_part
            })
            
            await self.session.send(text, end_of_turn=end_of_turn)
            
            # Check if we should transition parts
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            raise
    
    async def _handle_responses(self):
        """
        Handle responses from Gemini with Smart Selection tracking
        """
        try:
            async for message in self.session.receive():
                # Handle text response
                if message.text:
                    # Track for workflow
                    self.workflow_manager.track_response('maya', message.text)
                    
                    # Add to transcript
                    self.conversation_transcript.append({
                        'role': 'maya',
                        'content': message.text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'part': self.workflow_manager.state.current_part
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
                    logger.debug(f"Turn complete in Part {self.workflow_manager.state.current_part}")
                    
        except Exception as e:
            if not "cancelled" in str(e).lower():
                logger.error(f"Error handling responses: {e}")
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get full conversation transcript with part annotations"""
        return self.conversation_transcript
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary with Smart Selection metrics"""
        return self.workflow_manager.get_assessment_summary()
    
    async def close(self):
        """Close session and generate summary"""
        if self.session:
            # Get final summary
            summary = self.get_assessment_summary()
            logger.info(f"Assessment completed - Cost: {summary['cost_breakdown']['total']}")
            
            # Cancel response handler
            if self.response_task:
                self.response_task.cancel()
            
            # Close session
            await self.session.close()
            
        self.is_connected = False
        logger.info("Gemini Live session closed")


# Integration helper for Flask routes
def create_smart_selection_service(
    project_id: Optional[str] = None,
    region: str = 'us-central1'
) -> GeminiLiveServiceSmart:
    """
    Create a Smart Selection enabled Gemini Live service
    
    Returns:
        GeminiLiveServiceSmart instance ready for use
    """
    return GeminiLiveServiceSmart(
        project_id=project_id or os.environ.get('GOOGLE_CLOUD_PROJECT'),
        region=region
    )


async def run_smart_assessment(
    service: GeminiLiveServiceSmart,
    audio_data: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Run a complete Smart Selection assessment
    
    Args:
        service: Smart Selection Gemini service
        audio_data: Optional audio data to start with
    
    Returns:
        Assessment summary with cost breakdown
    """
    # Start conversation
    session = await service.start_maya_conversation_smart()
    
    # If audio provided, send it
    if audio_data:
        await session.send_audio(audio_data)
    
    # Simulate conversation (in production, this would be real-time)
    # ... handle real-time audio/text exchanges ...
    
    # Get summary before closing
    summary = session.get_assessment_summary()
    
    # Close session
    await session.close()
    
    return summary


# Cost projection for business planning
def project_monthly_costs(assessments_per_month: int) -> Dict[str, Any]:
    """
    Project monthly costs with Smart Selection
    
    Args:
        assessments_per_month: Number of assessments expected
    
    Returns:
        Cost projections and savings
    """
    # Smart Selection average cost (70% basic, 30% complex)
    smart_cost_per_assessment = 0.01 * 0.7 + 0.027 * 0.3  # ~$0.0181
    
    # All Flash cost
    flash_cost_per_assessment = 0.0588
    
    # Calculate
    smart_total = smart_cost_per_assessment * assessments_per_month
    flash_total = flash_cost_per_assessment * assessments_per_month
    savings = flash_total - smart_total
    
    return {
        'assessments': assessments_per_month,
        'smart_selection': {
            'per_assessment': f"${smart_cost_per_assessment:.4f}",
            'monthly_total': f"${smart_total:.2f}"
        },
        'all_flash': {
            'per_assessment': f"${flash_cost_per_assessment:.4f}",
            'monthly_total': f"${flash_total:.2f}"
        },
        'monthly_savings': f"${savings:.2f}",
        'savings_percentage': f"{(savings/flash_total)*100:.1f}%"
    }


if __name__ == "__main__":
    # Show cost projections
    print("=== Smart Selection Cost Projections ===\n")
    
    for count in [100, 500, 1000, 5000]:
        projection = project_monthly_costs(count)
        print(f"{count} assessments/month:")
        print(f"  Smart Selection: {projection['smart_selection']['monthly_total']}")
        print(f"  All Flash: {projection['all_flash']['monthly_total']}")
        print(f"  Savings: {projection['monthly_savings']} ({projection['savings_percentage']})\n")