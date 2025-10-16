"""
Flask routes for IELTS Listening Tests
Handles full test flow with instant scoring
"""
from flask import Blueprint, request, jsonify, session, Response
from listening_test_service import ListeningTestService
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
listening_routes = Blueprint('listening', __name__)

# Initialize service
listening_service = ListeningTestService()

# ============================================================================
# TEST ACCESS ENDPOINTS
# ============================================================================

@listening_routes.route('/api/listening/tests', methods=['GET'])
def get_available_tests():
    """
    Get list of available listening tests
    """
    try:
        test_type = request.args.get('type', 'all')  # academic, general, or all
        
        # For now, return hardcoded list
        # In production, query from DynamoDB
        tests = []
        
        if test_type in ['academic', 'all']:
            tests.append({
                'test_id': 'academic-listening-test-1',
                'title': 'Academic Listening Test 1',
                'type': 'academic',
                'duration': 30,
                'questions': 40,
                'sections': 4,
                'available': True
            })
            
            tests.append({
                'test_id': 'academic-listening-test-2',
                'title': 'Academic Listening Test 2',
                'type': 'academic',
                'duration': 30,
                'questions': 40,
                'sections': 4,
                'available': True
            })
        
        return jsonify({
            'success': True,
            'tests': tests,
            'count': len(tests)
        })
    
    except Exception as e:
        logger.error(f"Error fetching tests: {e}")
        return jsonify({'error': str(e)}), 500

@listening_routes.route('/api/listening/test/<test_id>', methods=['GET'])
def get_listening_test(test_id):
    """
    Get a specific listening test for user
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has access to this test
        # For now, allow all authenticated users
        
        # Get test data without answers
        test_data = listening_service.get_listening_test(test_id, user_id)
        
        if 'error' in test_data:
            return jsonify(test_data), 404
        
        return jsonify({
            'success': True,
            **test_data
        })
    
    except Exception as e:
        logger.error(f"Error fetching test {test_id}: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# TEST PROGRESS ENDPOINTS
# ============================================================================

@listening_routes.route('/api/listening/progress', methods=['POST'])
def update_progress():
    """
    Update user's progress during the test
    Auto-saves answers as user progresses
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        test_id = data.get('test_id')
        current_question = data.get('current_question', 1)
        answers = data.get('answers', {})
        time_remaining = data.get('time_remaining', 1800)  # seconds
        
        if not test_id:
            return jsonify({'error': 'Test ID required'}), 400
        
        # Update progress
        progress = listening_service.update_progress(
            test_id=test_id,
            user_id=user_id,
            current_question=current_question,
            answers=answers,
            time_remaining=time_remaining
        )
        
        return jsonify({
            'success': True,
            'progress': progress
        })
    
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return jsonify({'error': str(e)}), 500

@listening_routes.route('/api/listening/progress/<test_id>', methods=['GET'])
def get_progress(test_id):
    """
    Get user's current progress for a test
    Useful for resuming interrupted tests
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        progress_id = f"{user_id}#{test_id}"
        
        # Get progress from DynamoDB
        # For now, return mock data
        progress = {
            'test_id': test_id,
            'current_section': 1,
            'current_question': 1,
            'answers': {},
            'time_remaining': 1800,
            'status': 'not_started'
        }
        
        return jsonify({
            'success': True,
            'progress': progress
        })
    
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANSWER SUBMISSION & SCORING
# ============================================================================

@listening_routes.route('/api/listening/submit', methods=['POST'])
def submit_answers():
    """
    Submit answers and get instant score
    Uses answer key validation (no AI needed)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        test_id = data.get('test_id')
        user_answers = data.get('answers', {})
        
        if not test_id:
            return jsonify({'error': 'Test ID required'}), 400
        
        # Validate answers and calculate score
        results = listening_service.validate_answers(
            test_id=test_id,
            user_answers=user_answers,
            user_id=user_id
        )
        
        if 'error' in results:
            return jsonify(results), 400
        
        # Format response for UI
        response = {
            'success': True,
            'test_id': test_id,
            'score': {
                'correct': results['correct'],
                'incorrect': results['incorrect'],
                'unanswered': results['unanswered'],
                'total': results['total_questions'],
                'percentage': round((results['correct'] / results['total_questions']) * 100, 1)
            },
            'band_score': results['band_score'],
            'section_performance': results['section_performance'],
            'completed_at': results['completed_at']
        }
        
        # In practice mode, don't reveal correct answers
        # In review mode, can show them
        if data.get('mode') == 'review':
            response['review_enabled'] = True
            # Could add correct answers here if in review mode
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        return jsonify({'error': str(e)}), 500

@listening_routes.route('/api/listening/review/<test_id>', methods=['GET'])
def get_test_review(test_id):
    """
    Get test review with correct answers
    Only available after test completion
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has completed this test
        # For now, return placeholder
        
        return jsonify({
            'success': True,
            'message': 'Review feature coming soon',
            'test_id': test_id
        })
    
    except Exception as e:
        logger.error(f"Error fetching review: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AUDIO STREAMING ENDPOINTS
# ============================================================================

@listening_routes.route('/api/listening/audio/<test_id>/<int:section>', methods=['GET'])
def get_audio_url(test_id, section):
    """
    Get pre-signed URL for audio file
    URLs expire after test duration for security
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify user has access to this test
        # Generate pre-signed URL
        
        # For now, return placeholder
        audio_url = f"https://cloudfront.example.com/listening/{test_id}/section{section}.mp3"
        
        return jsonify({
            'success': True,
            'audio_url': audio_url,
            'expires_in': 3600  # 1 hour
        })
    
    except Exception as e:
        logger.error(f"Error generating audio URL: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# FULL TEST INTEGRATION
# ============================================================================

@listening_routes.route('/api/full-test/listening/start', methods=['POST'])
def start_full_test_listening():
    """
    Start listening component of full-length test
    Part of the complete IELTS practice test flow
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        full_test_id = data.get('full_test_id')
        test_type = data.get('test_type', 'academic')
        test_number = data.get('test_number', 1)
        
        # Get the appropriate listening test
        test_id = f"{test_type}-listening-test-{test_number}"
        
        # Initialize test for user
        test_data = listening_service.get_listening_test(test_id, user_id)
        
        if 'error' in test_data:
            return jsonify(test_data), 404
        
        # Track as part of full test
        session[f'full_test_{full_test_id}_listening'] = {
            'test_id': test_id,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'in_progress'
        }
        
        return jsonify({
            'success': True,
            'component': 'listening',
            'test_id': test_id,
            **test_data
        })
    
    except Exception as e:
        logger.error(f"Error starting full test listening: {e}")
        return jsonify({'error': str(e)}), 500

@listening_routes.route('/api/full-test/listening/complete', methods=['POST'])
def complete_full_test_listening():
    """
    Complete listening component and move to reading
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        full_test_id = data.get('full_test_id')
        test_id = data.get('test_id')
        user_answers = data.get('answers', {})
        
        # Validate and score
        results = listening_service.validate_answers(
            test_id=test_id,
            user_answers=user_answers,
            user_id=user_id
        )
        
        # Update full test progress
        session[f'full_test_{full_test_id}_listening']['status'] = 'completed'
        session[f'full_test_{full_test_id}_listening']['score'] = results['band_score']
        
        return jsonify({
            'success': True,
            'component': 'listening',
            'status': 'completed',
            'score': results['band_score'],
            'next_component': 'reading',
            'message': 'Listening test completed. Proceed to Reading test.'
        })
    
    except Exception as e:
        logger.error(f"Error completing listening: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ADMIN ENDPOINTS (for loading test data)
# ============================================================================

@listening_routes.route('/api/admin/listening/load-test', methods=['POST'])
def load_test_data():
    """
    Admin endpoint to load test data
    """
    try:
        # Check admin authorization
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        test_type = data.get('test_type', 'academic')
        test_number = data.get('test_number', 1)
        
        # Import and run the storage script
        from store_listening_test_1 import main as store_test
        result = store_test()
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        return jsonify({'error': str(e)}), 500