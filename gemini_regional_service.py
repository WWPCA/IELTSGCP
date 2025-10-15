"""
Gemini 2.5 Flash Live API Service with Regional Routing and DSQ
Implements Vertex AI Dynamic Shared Quota with intelligent regional selection
Cost: ~$0.025 per 14-minute session with global low-latency access
"""
import asyncio
import json
import logging
import os
import time
import hashlib
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import secrets

# Google Generative AI SDK
from google import genai
from google.genai.types import LiveConnectConfig, Modality, Blob

# Import workflow manager for Smart Selection
from ielts_workflow_manager import IELTSWorkflowManager, SmartSelectionOrchestrator

logger = logging.getLogger(__name__)

# ============================================================================
# REGIONAL CONFIGURATION
# ============================================================================

REGION_MAP = {
    # South Asia cluster - Mumbai region
    'IN': 'asia-south1', 'PK': 'asia-south1', 'BD': 'asia-south1', 
    'LK': 'asia-south1', 'NP': 'asia-south1', 'AF': 'asia-south1',
    
    # Southeast Asia cluster - Singapore region
    'SG': 'asia-southeast1', 'MY': 'asia-southeast1', 'TH': 'asia-southeast1',
    'ID': 'asia-southeast1', 'PH': 'asia-southeast1', 'VN': 'asia-southeast1',
    'KH': 'asia-southeast1', 'LA': 'asia-southeast1', 'MM': 'asia-southeast1',
    'BN': 'asia-southeast1', 'TL': 'asia-southeast1',
    
    # East Asia - Individual regions for data residency
    'KR': 'asia-northeast3',  # Seoul
    'JP': 'asia-northeast1',  # Tokyo
    'TW': 'asia-east1',       # Taiwan
    'HK': 'asia-east1',       # Taiwan (closest to HK)
    'MO': 'asia-east1',       # Taiwan (closest to Macau)
    'CN': 'asia-east1',       # Taiwan (if accessible)
    
    # Europe cluster - Belgium/Frankfurt split
    'GB': 'europe-west1', 'FR': 'europe-west1', 'DE': 'europe-west3',
    'IT': 'europe-west8', 'ES': 'europe-southwest1', 'NL': 'europe-west4',
    'PL': 'europe-central2', 'BE': 'europe-west1', 'CH': 'europe-west6',
    'AT': 'europe-west3', 'CZ': 'europe-west3', 'HU': 'europe-west3',
    
    # Eastern Europe - Frankfurt
    'RU': 'europe-west3', 'UA': 'europe-west3', 'TR': 'europe-west3',
    'RO': 'europe-west3', 'BG': 'europe-west3', 'RS': 'europe-west3',
    
    # Nordic - Finland
    'SE': 'europe-north1', 'NO': 'europe-north1', 'DK': 'europe-north1',
    'FI': 'europe-north1', 'IS': 'europe-north1',
    
    # Middle East - Split between Dammam and Tel Aviv
    'SA': 'me-central2', 'AE': 'me-central2', 'KW': 'me-central2',
    'QA': 'me-central2', 'BH': 'me-central2', 'OM': 'me-central2',
    'IL': 'me-west1', 'JO': 'me-west1', 'LB': 'me-west1',
    
    # Africa - Split regions
    'ZA': 'africa-south1', 'NG': 'europe-west1', 'EG': 'europe-west1',
    'KE': 'europe-west1', 'GH': 'europe-west1', 'ET': 'europe-west1',
    'MA': 'europe-southwest1', 'TN': 'europe-west8', 'DZ': 'europe-west1',
    
    # Americas - US Central with some regional optimization
    'US': 'us-central1', 'CA': 'northamerica-northeast1', 
    'MX': 'us-south1', 'BR': 'southamerica-east1',
    'AR': 'southamerica-east1', 'CL': 'southamerica-east1',
    'CO': 'us-central1', 'PE': 'us-central1', 'VE': 'us-central1',
    
    # Australia/Oceania
    'AU': 'australia-southeast1', 'NZ': 'australia-southeast1',
    'FJ': 'australia-southeast1', 'PG': 'australia-southeast1',
}

# Fallback regions for better coverage
REGIONAL_FALLBACKS = {
    'asia': 'asia-southeast1',      # Singapore as Asia hub
    'europe': 'europe-west1',        # Belgium as Europe hub
    'americas': 'us-central1',       # Iowa as Americas hub
    'africa': 'europe-west1',        # Belgium for Africa
    'oceania': 'australia-southeast1', # Sydney for Oceania
}

# ============================================================================
# REGION HEALTH MONITORING
# ============================================================================

class RegionHealthMonitor:
    """Monitors health of regional endpoints and provides failover"""
    
    def __init__(self):
        self.region_health = {}
        self.error_counts = defaultdict(int)
        self.latency_history = defaultdict(list)
        self.last_health_check = {}
        
    def record_success(self, region: str, latency_ms: float):
        """Record successful request"""
        self.error_counts[region] = max(0, self.error_counts[region] - 1)
        self.latency_history[region].append(latency_ms)
        
        # Keep only last 100 latency measurements
        if len(self.latency_history[region]) > 100:
            self.latency_history[region] = self.latency_history[region][-100:]
        
        # Mark as healthy
        self.region_health[region] = {
            'healthy': True,
            'avg_latency': sum(self.latency_history[region]) / len(self.latency_history[region]),
            'last_check': time.time()
        }
    
    def record_error(self, region: str, error_type: str = 'general'):
        """Record failed request"""
        self.error_counts[region] += 1
        
        # Mark unhealthy after 5 consecutive errors
        if self.error_counts[region] >= 5:
            self.region_health[region] = {
                'healthy': False,
                'error_type': error_type,
                'until': time.time() + 300,  # Unhealthy for 5 minutes
                'last_check': time.time()
            }
            logger.warning(f"Region {region} marked unhealthy: {error_type}")
    
    def is_healthy(self, region: str) -> bool:
        """Check if region is healthy"""
        if region not in self.region_health:
            return True  # Assume healthy if not tested
        
        health = self.region_health[region]
        if not health['healthy']:
            # Check if unhealthy period expired
            if time.time() > health.get('until', 0):
                self.region_health[region]['healthy'] = True
                self.error_counts[region] = 0
                return True
            return False
        
        return True
    
    def get_healthy_region(self, preferred_region: str, fallback_global: bool = True) -> str:
        """Get healthy region with fallback"""
        if self.is_healthy(preferred_region):
            return preferred_region
        
        # Try regional fallback
        for continent, hub in REGIONAL_FALLBACKS.items():
            if self.is_healthy(hub):
                logger.info(f"Using regional fallback {hub} instead of unhealthy {preferred_region}")
                return hub
        
        # Use global endpoint as last resort
        if fallback_global:
            logger.info(f"Using global endpoint due to regional failures")
            return 'global'
        
        # Force use preferred region if no fallback allowed
        return preferred_region
    
    def get_latency_stats(self, region: str) -> Optional[Dict[str, float]]:
        """Get latency statistics for a region"""
        if region not in self.latency_history or not self.latency_history[region]:
            return None
        
        latencies = self.latency_history[region]
        return {
            'avg': sum(latencies) / len(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'p50': sorted(latencies)[len(latencies) // 2],
            'p95': sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies)
        }

# ============================================================================
# LATENCY-BASED REGION SELECTION
# ============================================================================

class RegionLatencyOptimizer:
    """Optimizes region selection based on latency testing"""
    
    def __init__(self, health_monitor: RegionHealthMonitor):
        self.health_monitor = health_monitor
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    async def test_region_latency(self, region: str) -> Tuple[str, float]:
        """Test latency to a specific region"""
        try:
            start = time.time()
            
            # Simulate API endpoint ping (replace with actual endpoint test)
            # In production, you'd make a lightweight API call to test connectivity
            endpoint = f"https://{region}-aiplatform.googleapis.com/v1/projects/test/locations/{region}"
            
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    endpoint,
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    latency = (time.time() - start) * 1000
                    return region, latency
                    
        except Exception as e:
            logger.debug(f"Latency test failed for {region}: {e}")
            return region, 9999  # High latency for failed regions
    
    async def get_optimal_region(
        self,
        country_code: str,
        test_latency: bool = False,
        use_global_fallback: bool = True
    ) -> str:
        """Get optimal region with optional latency testing"""
        
        # Get primary region from mapping
        primary_region = REGION_MAP.get(country_code)
        
        if not primary_region:
            # Try continental fallback
            primary_region = self._get_continental_fallback(country_code)
        
        if not primary_region:
            return 'global' if use_global_fallback else 'us-central1'
        
        # Quick return if not testing latency
        if not test_latency:
            return self.health_monitor.get_healthy_region(primary_region, use_global_fallback)
        
        # Test latency to multiple candidate regions
        candidates = [primary_region]
        
        # Add nearby regions as candidates
        if primary_region.startswith('asia'):
            candidates.extend(['asia-southeast1', 'asia-northeast1'])
        elif primary_region.startswith('europe'):
            candidates.extend(['europe-west1', 'europe-west4'])
        elif primary_region.startswith('us'):
            candidates.extend(['us-east1', 'us-west1'])
        
        # Add global if enabled
        if use_global_fallback:
            candidates.append('global')
        
        # Remove duplicates and unhealthy regions
        candidates = list(set(
            c for c in candidates 
            if self.health_monitor.is_healthy(c)
        ))[:5]  # Test max 5 regions
        
        # Test all candidates in parallel
        tasks = [self.test_region_latency(region) for region in candidates]
        results = await asyncio.gather(*tasks)
        
        # Select region with lowest latency
        best_region = min(results, key=lambda x: x[1])
        
        if best_region[1] < 9999:
            logger.info(f"Selected {best_region[0]} with {best_region[1]:.0f}ms latency for {country_code}")
            return best_region[0]
        
        # Fallback if all tests failed
        return 'global' if use_global_fallback else primary_region
    
    def _get_continental_fallback(self, country_code: str) -> Optional[str]:
        """Get continental fallback for unknown country"""
        # Simple continent detection based on country code patterns
        if country_code in ['AS', 'AP']:  # Generic Asia-Pacific codes
            return 'asia-southeast1'
        elif country_code in ['EU', 'EP']:  # Generic Europe codes
            return 'europe-west1'
        elif country_code in ['NA', 'SA']:  # Generic Americas codes
            return 'us-central1'
        return None

# ============================================================================
# ENHANCED GEMINI LIVE SERVICE WITH DSQ
# ============================================================================

class GeminiRegionalService:
    """
    Enhanced Gemini Live service with regional routing and DSQ support
    Uses Vertex AI endpoints for Dynamic Shared Quota management
    """
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        # Initialize monitoring and optimization
        self.health_monitor = RegionHealthMonitor()
        self.latency_optimizer = RegionLatencyOptimizer(self.health_monitor)
        
        # Cache for regional clients
        self.regional_clients = {}
        
        # Smart Selection models
        self.models = {
            'flash-lite': 'gemini-2.5-flash-lite',
            'flash': 'gemini-2.5-flash',
            'flash-native': 'gemini-2.5-flash-native-audio-preview-09-2025'
        }
        
        logger.info(f"Gemini Regional Service initialized - project: {self.project_id}")
    
    def _get_or_create_client(self, region: str) -> genai.Client:
        """Get or create regional client with caching"""
        if region not in self.regional_clients:
            # Configure for Vertex AI with DSQ
            os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
            os.environ['GOOGLE_CLOUD_LOCATION'] = region
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'  # Enable DSQ
            
            # Create regional client
            self.regional_clients[region] = genai.Client()
            logger.info(f"Created Vertex AI client for region: {region}")
        
        return self.regional_clients[region]
    
    async def start_maya_conversation_regional(
        self,
        country_code: str = None,
        assessment_type: str = 'speaking',
        on_text_response: Optional[Callable[[str], None]] = None,
        on_audio_response: Optional[Callable[[bytes], None]] = None,
        content_moderation_callback: Optional[Callable[[str], bool]] = None,
        test_latency: bool = False,
        use_global_fallback: bool = True
    ) -> 'GeminiRegionalSession':
        """
        Start Maya conversation with regional optimization
        
        Args:
            country_code: ISO 3166-1 alpha-2 country code for regional routing
            assessment_type: Type of IELTS assessment
            on_text_response: Callback for text transcripts
            on_audio_response: Callback for audio chunks
            content_moderation_callback: Content moderation check
            test_latency: Whether to test latency before selecting region
            use_global_fallback: Whether to use global endpoint as fallback
        
        Returns:
            GeminiRegionalSession with optimal regional routing
        """
        
        # Determine optimal region
        if country_code:
            region = await self.latency_optimizer.get_optimal_region(
                country_code,
                test_latency=test_latency,
                use_global_fallback=use_global_fallback
            )
        else:
            region = 'global' if use_global_fallback else 'us-central1'
        
        logger.info(f"Starting assessment for {country_code or 'unknown'} using region: {region}")
        
        # Get regional client
        client = self._get_or_create_client(region)
        
        # Create workflow manager for this session
        workflow_manager = IELTSWorkflowManager()
        
        # Start with Part 1 configuration
        config = workflow_manager.update_state_for_part(1)
        
        # Create Live config with optimized prompt
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=config['prompt']
        )
        
        # Create regional session
        session = GeminiRegionalSession(
            client=client,
            model_id=config['model'],
            config=live_config,
            workflow_manager=workflow_manager,
            region=region,
            health_monitor=self.health_monitor,
            on_text_response=on_text_response,
            on_audio_response=on_audio_response,
            content_moderation_callback=content_moderation_callback
        )
        
        # Track start time for latency monitoring
        start_time = time.time()
        
        try:
            await session.connect()
            
            # Record successful connection
            connect_latency = (time.time() - start_time) * 1000
            self.health_monitor.record_success(region, connect_latency)
            
            logger.info(f"Connected to {region} in {connect_latency:.0f}ms")
            
        except Exception as e:
            # Record failure
            self.health_monitor.record_error(region, str(type(e).__name__))
            
            # Try fallback if available
            if use_global_fallback and region != 'global':
                logger.warning(f"Failed to connect to {region}, trying global endpoint")
                return await self.start_maya_conversation_regional(
                    country_code=country_code,
                    assessment_type=assessment_type,
                    on_text_response=on_text_response,
                    on_audio_response=on_audio_response,
                    content_moderation_callback=content_moderation_callback,
                    test_latency=False,  # Don't test again
                    use_global_fallback=False  # Prevent infinite recursion
                )
            raise
        
        return session
    
    def get_regional_analytics(self) -> Dict[str, Any]:
        """Get analytics on regional usage and performance"""
        analytics = {
            'regions': {},
            'health_status': {},
            'recommendations': []
        }
        
        for region in set(REGION_MAP.values()):
            # Get health status
            analytics['health_status'][region] = {
                'healthy': self.health_monitor.is_healthy(region),
                'error_count': self.health_monitor.error_counts[region]
            }
            
            # Get latency stats
            latency_stats = self.health_monitor.get_latency_stats(region)
            if latency_stats:
                analytics['regions'][region] = latency_stats
        
        # Add recommendations
        unhealthy_regions = [
            r for r, status in analytics['health_status'].items()
            if not status['healthy']
        ]
        
        if unhealthy_regions:
            analytics['recommendations'].append(
                f"Consider investigating issues in: {', '.join(unhealthy_regions)}"
            )
        
        return analytics


class GeminiRegionalSession:
    """
    Gemini Live session with regional optimization and health tracking
    """
    
    def __init__(
        self,
        client: genai.Client,
        model_id: str,
        config: LiveConnectConfig,
        workflow_manager: IELTSWorkflowManager,
        region: str,
        health_monitor: RegionHealthMonitor,
        on_text_response: Optional[Callable] = None,
        on_audio_response: Optional[Callable] = None,
        content_moderation_callback: Optional[Callable] = None
    ):
        self.client = client
        self.model_id = model_id
        self.config = config
        self.workflow_manager = workflow_manager
        self.region = region
        self.health_monitor = health_monitor
        self.on_text_response = on_text_response
        self.on_audio_response = on_audio_response
        self.content_moderation_callback = content_moderation_callback
        
        self.session = None
        self.is_connected = False
        self.conversation_transcript = []
        self.audio_buffer = []
        self.response_task = None
        self.messages_in_current_part = 0
        self.session_start_time = time.time()
    
    async def connect(self):
        """Connect to Gemini Live with regional endpoint"""
        try:
            self.session = self.client.live.connect(
                model=self.model_id,
                config=self.config
            )
            self.is_connected = True
            
            # Start response handler
            self.response_task = asyncio.create_task(self._handle_responses())
            
            logger.info(f"Connected to Gemini Live in region: {self.region}")
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.region}: {e}")
            raise
    
    async def _handle_responses(self):
        """Handle responses with latency tracking"""
        try:
            async for message in self.session.receive():
                response_time = time.time()
                
                # Handle text response
                if message.text:
                    self.workflow_manager.track_response('maya', message.text)
                    
                    self.conversation_transcript.append({
                        'role': 'maya',
                        'content': message.text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'part': self.workflow_manager.state.current_part,
                        'region': self.region
                    })
                    
                    if self.on_text_response:
                        self.on_text_response(message.text)
                
                # Handle audio response
                if message.data:
                    self.audio_buffer.append(message.data)
                    
                    if self.on_audio_response:
                        self.on_audio_response(message.data)
                
                # Track response latency
                latency = (time.time() - response_time) * 1000
                if latency < 5000:  # Only track reasonable latencies
                    self.health_monitor.record_success(self.region, latency)
                
                # Check if turn is complete
                if message.server_content and message.server_content.turn_complete:
                    logger.debug(f"Turn complete in Part {self.workflow_manager.state.current_part} via {self.region}")
                    
        except Exception as e:
            if not "cancelled" in str(e).lower():
                logger.error(f"Error handling responses from {self.region}: {e}")
                self.health_monitor.record_error(self.region, str(type(e).__name__))
    
    # Include all other methods from GeminiLiveSessionSmart
    async def send_audio(self, audio_data: bytes, mime_type: str = 'audio/wav'):
        """Send audio with regional tracking"""
        if not self.is_connected:
            raise RuntimeError("Session not connected")
        
        try:
            start_time = time.time()
            
            # Track response for workflow
            self.workflow_manager.track_response('candidate', f"[Audio input {len(audio_data)} bytes]")
            self.messages_in_current_part += 1
            
            # Convert audio to required format
            audio_blob = Blob(
                data=audio_data,
                mime_type=mime_type
            )
            
            await self.session.send_realtime_input(audio=audio_blob)
            
            # Track send latency
            send_latency = (time.time() - start_time) * 1000
            self.health_monitor.record_success(self.region, send_latency)
            
            # Check if we should transition parts
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send audio to {self.region}: {e}")
            self.health_monitor.record_error(self.region, 'send_audio_error')
            raise
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """Send text with content moderation"""
        if not self.is_connected:
            raise RuntimeError("Session not connected")
        
        try:
            # Content moderation check
            if self.content_moderation_callback:
                if not self.content_moderation_callback(text):
                    logger.warning(f"Content moderation blocked text: {text[:50]}...")
                    return
            
            # Track response
            self.workflow_manager.track_response('candidate', text)
            self.messages_in_current_part += 1
            
            # Add to transcript
            self.conversation_transcript.append({
                'role': 'candidate',
                'content': text,
                'timestamp': datetime.utcnow().isoformat(),
                'part': self.workflow_manager.state.current_part,
                'region': self.region
            })
            
            await self.session.send(text, end_of_turn=end_of_turn)
            
            # Check transitions
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            raise
    
    async def check_and_transition_parts(self):
        """Check if it's time to transition to next IELTS part"""
        if self.workflow_manager.should_transition():
            next_part = self.workflow_manager.state.current_part + 1
            
            if next_part <= 3:
                config = self.workflow_manager.update_state_for_part(next_part)
                await self.switch_model(config['model'], config['prompt'])
                
                logger.info(f"Transitioned to Part {next_part} with {config['model']}")
                
                if self.on_text_response:
                    self.on_text_response(f"[Transitioning to Part {next_part}]")
                
                return True
        return False
    
    async def switch_model(self, new_model: str, new_prompt: str):
        """Switch to different model during assessment"""
        try:
            # Close current session
            if self.session:
                await self.session.close()
            
            # Update config
            self.config = LiveConnectConfig(
                response_modalities=[Modality.AUDIO],
                system_instruction=new_prompt
            )
            
            # Reconnect with new model
            self.model_id = new_model
            self.session = self.client.live.connect(
                model=self.model_id,
                config=self.config
            )
            
            self.messages_in_current_part = 0
            logger.info(f"Switched to {new_model} in {self.region}")
            
        except Exception as e:
            logger.error(f"Failed to switch model in {self.region}: {e}")
            self.health_monitor.record_error(self.region, 'model_switch_error')
            raise
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get full conversation transcript with regional metadata"""
        return self.conversation_transcript
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary with regional performance metrics"""
        duration_minutes = (time.time() - self.session_start_time) / 60
        
        summary = self.workflow_manager.get_assessment_summary()
        
        # Add regional metadata
        summary['regional_info'] = {
            'region': self.region,
            'latency_stats': self.health_monitor.get_latency_stats(self.region),
            'session_duration': duration_minutes
        }
        
        return summary
    
    async def close(self):
        """Close session and clean up"""
        try:
            self.is_connected = False
            
            if self.response_task:
                self.response_task.cancel()
                
            if self.session:
                await self.session.close()
                
            logger.info(f"Closed session in {self.region} after {(time.time() - self.session_start_time) / 60:.1f} minutes")
            
        except Exception as e:
            logger.error(f"Error closing session: {e}")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_regional_gemini_service(
    project_id: Optional[str] = None
) -> GeminiRegionalService:
    """
    Factory function to create regional Gemini service
    
    Args:
        project_id: Google Cloud project ID
    
    Returns:
        Configured GeminiRegionalService instance
    """
    return GeminiRegionalService(project_id=project_id)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def example_usage():
    """Example of using regional Gemini service"""
    
    # Create service
    service = create_regional_gemini_service()
    
    # Start assessment for user in India
    session = await service.start_maya_conversation_regional(
        country_code='IN',  # Will use asia-south1 (Mumbai)
        assessment_type='speaking',
        test_latency=True,  # Test latency for optimal selection
        use_global_fallback=True  # Use global if regional fails
    )
    
    # Send audio
    audio_data = b"..."  # Your audio bytes
    await session.send_audio(audio_data)
    
    # Get results
    transcript = session.get_transcript()
    summary = session.get_assessment_summary()
    
    # Close session
    await session.close()
    
    # Get regional analytics
    analytics = service.get_regional_analytics()
    print(f"Regional performance: {analytics}")


if __name__ == "__main__":
    asyncio.run(example_usage())