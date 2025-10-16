"""
Flask routes for IELTS Reading Tests
Handles full test flow with instant scoring
"""
from flask import Blueprint, request, jsonify, session, Response
from reading_test_service import ReadingTestService
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
reading_routes = Blueprint('reading', __name__)

# Initialize service
reading_service = ReadingTestService()

# ============================================================================
# TEST ACCESS ENDPOINTS
# ============================================================================

@reading_routes.route('/api/reading/tests', methods=['GET'])
def get_available_tests():
    """
    Get list of available reading tests
    """
    try:
        test_type = request.args.get('type', 'all')  # academic, general, or all
        
        # For now, return hardcoded list
        # In production, query from DynamoDB
        tests = []
        
        if test_type in ['academic', 'all']:
            tests.append({
                'test_id': 'academic-reading-test-1',
                'title': 'Academic Reading Test 1',
                'type': 'academic',
                'duration': 60,
                'questions': 40,
                'passages': 3,
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

@reading_routes.route('/api/reading/test/<test_id>', methods=['GET'])
def get_reading_test(test_id):
    """
    Get a specific reading test for user
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get test data without answers
        test_data = reading_service.get_reading_test(test_id, user_id)
        
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

@reading_routes.route('/api/reading/progress', methods=['POST'])
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
        time_remaining = data.get('time_remaining', 3600)  # seconds
        
        if not test_id:
            return jsonify({'error': 'Test ID required'}), 400
        
        # Update progress
        progress = reading_service.update_progress(
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

@reading_routes.route('/api/reading/progress/<test_id>', methods=['GET'])
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
            'current_passage': 1,
            'current_question': 1,
            'answers': {},
            'time_remaining': 3600,
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

@reading_routes.route('/api/reading/submit', methods=['POST'])
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
        results = reading_service.validate_answers(
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
            'passage_performance': results['passage_performance'],
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

@reading_routes.route('/api/reading/review/<test_id>', methods=['GET'])
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
# FULL TEST INTEGRATION
# ============================================================================

@reading_routes.route('/api/full-test/reading/start', methods=['POST'])
def start_full_test_reading():
    """
    Start reading component of full-length test
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
        
        # Get the appropriate reading test
        test_id = f"{test_type}-reading-test-{test_number}"
        
        # Initialize test for user
        test_data = reading_service.get_reading_test(test_id, user_id)
        
        if 'error' in test_data:
            return jsonify(test_data), 404
        
        # Track as part of full test
        session[f'full_test_{full_test_id}_reading'] = {
            'test_id': test_id,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'in_progress'
        }
        
        return jsonify({
            'success': True,
            'component': 'reading',
            'test_id': test_id,
            **test_data
        })
    
    except Exception as e:
        logger.error(f"Error starting full test reading: {e}")
        return jsonify({'error': str(e)}), 500

@reading_routes.route('/api/full-test/reading/complete', methods=['POST'])
def complete_full_test_reading():
    """
    Complete reading component and move to writing
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
        results = reading_service.validate_answers(
            test_id=test_id,
            user_answers=user_answers,
            user_id=user_id
        )
        
        # Update full test progress
        session[f'full_test_{full_test_id}_reading']['status'] = 'completed'
        session[f'full_test_{full_test_id}_reading']['score'] = results['band_score']
        
        return jsonify({
            'success': True,
            'component': 'reading',
            'status': 'completed',
            'score': results['band_score'],
            'next_component': 'writing',
            'message': 'Reading test completed. Proceed to Writing test.'
        })
    
    except Exception as e:
        logger.error(f"Error completing reading: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# FULL ACADEMIC TEST PACKAGE ENDPOINT
# ============================================================================

@reading_routes.route('/api/full-test/academic/start', methods=['POST'])
def start_full_academic_test():
    """
    Start a complete Academic IELTS test (Listening + Reading + Writing + Speaking)
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Generate unique full test ID
        full_test_id = f"full-academic-{user_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize full test session
        session[f'full_test_{full_test_id}'] = {
            'test_id': full_test_id,
            'test_type': 'academic',
            'components': {
                'listening': {'status': 'pending', 'score': None},
                'reading': {'status': 'pending', 'score': None},
                'writing': {'status': 'pending', 'score': None},
                'speaking': {'status': 'pending', 'score': None}
            },
            'started_at': datetime.utcnow().isoformat(),
            'current_component': 'listening'
        }
        
        return jsonify({
            'success': True,
            'full_test_id': full_test_id,
            'test_type': 'academic',
            'components': ['listening', 'reading', 'writing', 'speaking'],
            'total_duration': '2 hours 45 minutes',
            'message': 'Full Academic IELTS test initialized. Starting with Listening test.'
        })
    
    except Exception as e:
        logger.error(f"Error starting full test: {e}")
        return jsonify({'error': str(e)}), 500

@reading_routes.route('/api/full-test/<full_test_id>/results', methods=['GET'])
def get_full_test_results(full_test_id):
    """
    Get complete results for a full IELTS test
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get test session
        test_session = session.get(f'full_test_{full_test_id}')
        if not test_session:
            return jsonify({'error': 'Test not found'}), 404
        
        # Calculate overall band score
        scores = []
        for component in ['listening', 'reading', 'writing', 'speaking']:
            score = test_session['components'][component]['score']
            if score:
                scores.append(float(score))
        
        if scores:
            overall_band = sum(scores) / len(scores)
            # Round to nearest 0.5
            overall_band = round(overall_band * 2) / 2
        else:
            overall_band = None
        
        return jsonify({
            'success': True,
            'full_test_id': full_test_id,
            'test_type': test_session['test_type'],
            'components': test_session['components'],
            'overall_band_score': overall_band,
            'completed_at': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error fetching full test results: {e}")
        return jsonify({'error': str(e)}), 500