"""
Hybrid Architecture Integration Routes
Nova Micro (text) + Gemini Live API (audio)
"""
from flask import Flask, request, jsonify, session, Response
from gemini_live_audio_service import GeminiLiveService
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Initialize Gemini Live service for audio
gemini_service = GeminiLiveService(
    project_id=os.environ.get('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
    region='us-central1'
)

# Store active Gemini Live sessions
active_sessions: Dict[str, Any] = {}


# ============================================================================
# SPEAKING ASSESSMENT - Real-Time Audio with Gemini Live API
# ============================================================================

def start_speaking_assessment_route(app: Flask):
    """
    Start real-time speaking assessment using Gemini Live API
    Cost: $0.00075-0.0042 per minute
    """
    
    @app.route('/api/speaking/start', methods=['POST'])
    def start_speaking():
        """Initialize Gemini Live session for real-time conversation with Maya"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Not authenticated'}), 401
            
            # Get assessment details
            data = request.get_json()
            assessment_type = data.get('assessment_type', 'speaking_part1')
            product_id = data.get('product_id')
            
            # Verify user has purchased speaking assessment
            # ... add your purchase verification logic here ...
            
            # Define callbacks for handling Gemini responses
            def on_text_response(text: str):
                """Handle transcription from Gemini"""
                logger.info(f"Maya transcript: {text}")
                # Store transcript in session
                if user_id in active_sessions:
                    active_sessions[user_id]['transcript'].append({
                        'role': 'maya',
                        'text': text,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            def on_audio_response(audio_data: bytes):
                """Handle audio from Gemini (Maya's voice)"""
                # Stream to client via WebSocket or store for playback
                if user_id in active_sessions:
                    active_sessions[user_id]['audio_chunks'].append(audio_data)
            
            def content_moderation(text: str) -> bool:
                """Check if content is appropriate"""
                # Add content moderation logic
                inappropriate_keywords = ['inappropriate', 'offensive', 'harmful']
                return not any(keyword in text.lower() for keyword in inappropriate_keywords)
            
            # Start Gemini Live session (async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            live_session = loop.run_until_complete(
                gemini_service.start_maya_conversation(
                    assessment_type=assessment_type,
                    on_text_response=on_text_response,
                    on_audio_response=on_audio_response,
                    content_moderation_callback=content_moderation
                )
            )
            
            # Store session
            active_sessions[user_id] = {
                'session': live_session,
                'loop': loop,
                'transcript': [],
                'audio_chunks': [],
                'started_at': datetime.utcnow().isoformat(),
                'assessment_type': assessment_type,
                'product_id': product_id
            }
            
            return jsonify({
                'success': True,
                'session_id': user_id,
                'message': 'Speaking session started with Maya',
                'cost_per_minute': 0.00075  # Flash-Lite pricing
            })
            
        except Exception as e:
            logger.error(f"Failed to start speaking session: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/speaking/audio', methods=['POST'])
    def send_audio():
        """Send user audio to Gemini Live API"""
        try:
            user_id = session.get('user_id')
            if not user_id or user_id not in active_sessions:
                return jsonify({'error': 'No active session'}), 400
            
            # Get audio data from request
            audio_data = request.data
            mime_type = request.headers.get('Content-Type', 'audio/wav')
            
            # Send to Gemini Live
            session_data = active_sessions[user_id]
            loop = session_data['loop']
            live_session = session_data['session']
            
            loop.run_until_complete(
                live_session.send_audio(audio_data, mime_type=mime_type)
            )
            
            return jsonify({'success': True, 'message': 'Audio sent to Maya'})
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/speaking/end', methods=['POST'])
    def end_speaking():
        """
        End Gemini Live session and generate feedback with Nova Micro
        This is where the hybrid architecture shines:
        - Gemini Live: Real-time conversation ($0.00075/min)
        - Nova Micro: Text feedback generation ($0.000105 per assessment)
        """
        try:
            user_id = session.get('user_id')
            if not user_id or user_id not in active_sessions:
                return jsonify({'error': 'No active session'}), 400
            
            session_data = active_sessions[user_id]
            live_session = session_data['session']
            loop = session_data['loop']
            
            # Get full transcript from Gemini session
            transcript = live_session.get_transcript()
            
            # Close Gemini Live session (stop charging per-minute cost)
            loop.run_until_complete(live_session.close())
            loop.close()
            
            # Remove from active sessions
            del active_sessions[user_id]
            
            # Format transcript for Nova Micro
            transcript_text = "\n".join([
                f"{msg.get('role', 'user').upper()}: {msg.get('content', msg.get('text', ''))}"
                for msg in transcript
            ])
            
            # Generate detailed feedback using Nova Micro (much cheaper!)
            # Import from your existing Nova Micro implementation
            from production_final.lambda_function import generate_maya_response
            
            feedback = generate_maya_response(
                transcript=transcript_text,
                assessment_type=session_data['assessment_type']
            )
            
            # Store results in database
            # ... add your database storage logic here ...
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'feedback': feedback,
                'duration_minutes': calculate_duration(session_data['started_at']),
                'cost_breakdown': {
                    'gemini_live': '$0.00075/min',
                    'nova_micro_feedback': '$0.000105',
                    'total_estimated': calculate_cost(session_data['started_at'])
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to end speaking session: {e}")
            return jsonify({'error': str(e)}), 500


# ============================================================================
# WRITING ASSESSMENT - Text Evaluation with Nova Micro
# ============================================================================

def writing_assessment_routes(app: Flask):
    """
    Writing assessment using Nova Micro (cheapest text option)
    Cost: $0.000105 per assessment
    """
    
    @app.route('/api/writing/evaluate', methods=['POST'])
    def evaluate_writing():
        """Evaluate writing essay with Nova Micro"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            essay = data.get('essay')
            task_number = data.get('task_number', 2)
            assessment_type = data.get('assessment_type', 'academic_writing')
            product_id = data.get('product_id')
            
            # Validate essay
            if not essay or len(essay.split()) < 150:
                return jsonify({'error': 'Essay too short (minimum 150 words)'}), 400
            
            # Get appropriate rubric
            from assessment_criteria.writing_criteria import (
                WRITING_TASK1_BAND_DESCRIPTORS,
                WRITING_TASK2_BAND_DESCRIPTORS
            )
            
            rubric = WRITING_TASK1_BAND_DESCRIPTORS if task_number == 1 else WRITING_TASK2_BAND_DESCRIPTORS
            task_prompt = get_task_prompt(task_number, assessment_type)
            
            # Evaluate with Nova Micro (cheapest option for text)
            from production_final.lambda_function import evaluate_writing_with_nova_micro
            
            result = evaluate_writing_with_nova_micro(
                essay_text=essay,
                task_prompt=task_prompt,
                rubric=rubric,
                assessment_type=assessment_type
            )
            
            # Add metadata
            result['word_count'] = len(essay.split())
            result['task_number'] = task_number
            result['assessed_at'] = datetime.utcnow().isoformat()
            result['cost_estimate'] = '$0.000105'
            
            # Store in database
            # ... add your database storage logic here ...
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Failed to evaluate writing: {e}")
            return jsonify({'error': str(e)}), 500


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_task_prompt(task_number: int, assessment_type: str) -> str:
    """Get IELTS writing task prompt"""
    # Add your task prompt logic here
    if task_number == 1:
        return "Describe the chart/graph/diagram..."
    else:
        return "To what extent do you agree or disagree..."


def calculate_duration(started_at: str) -> float:
    """Calculate session duration in minutes"""
    start_time = datetime.fromisoformat(started_at)
    duration = (datetime.utcnow() - start_time).total_seconds() / 60
    return round(duration, 2)


def calculate_cost(started_at: str) -> str:
    """Calculate total cost for session"""
    duration = calculate_duration(started_at)
    gemini_cost = duration * 0.00075  # Flash-Lite pricing
    nova_cost = 0.000105  # Feedback generation
    total = gemini_cost + nova_cost
    return f"${total:.6f}"


# ============================================================================
# WEBSOCKET SUPPORT (Optional - for real-time audio streaming)
# ============================================================================

def setup_websocket_routes(app: Flask):
    """
    Optional: WebSocket routes for real-time audio streaming
    Requires flask-socketio or similar
    """
    
    try:
        from flask_socketio import SocketIO, emit
        
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        @socketio.on('start_speaking')
        def handle_start_speaking(data):
            """Start speaking session via WebSocket"""
            user_id = session.get('user_id')
            assessment_type = data.get('assessment_type', 'speaking_part1')
            
            # Start Gemini Live session
            # ... (same logic as HTTP route above) ...
            
            emit('session_started', {'success': True})
        
        @socketio.on('audio_chunk')
        def handle_audio_chunk(audio_data):
            """Receive audio chunk from client"""
            user_id = session.get('user_id')
            
            if user_id in active_sessions:
                session_data = active_sessions[user_id]
                loop = session_data['loop']
                live_session = session_data['session']
                
                # Send to Gemini Live
                loop.run_until_complete(
                    live_session.send_audio(audio_data, mime_type='audio/wav')
                )
        
        @socketio.on('maya_audio')
        def handle_maya_audio(audio_data):
            """Stream Maya's audio to client"""
            emit('maya_speaks', {'audio': audio_data})
        
        return socketio
        
    except ImportError:
        logger.warning("flask-socketio not installed, WebSocket support disabled")
        return None


# ============================================================================
# REGISTRATION
# ============================================================================

def register_hybrid_routes(app: Flask):
    """Register all hybrid architecture routes"""
    start_speaking_assessment_route(app)
    writing_assessment_routes(app)
    
    # Optional WebSocket support
    socketio = setup_websocket_routes(app)
    
    logger.info("Hybrid architecture routes registered successfully")
    logger.info("- Nova Micro: Text assessment ($0.000105 per assessment)")
    logger.info("- Gemini Live: Audio conversations ($0.00075-0.0042 per minute)")
    
    return socketio


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == '__main__':
    from flask import Flask
    
    app = Flask(__name__)
    app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret')
    
    # Register routes
    socketio = register_hybrid_routes(app)
    
    # Run app
    if socketio:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
