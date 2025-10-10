"""
Example: How to use Gemini IELTS Service in app.py
This shows the clean integration approach for your hybrid AWS + Gemini architecture
"""
import asyncio
from gemini_ielts_service import gemini_service

# EXAMPLE 1: Evaluate Speaking Assessment
async def example_speaking_evaluation():
    """Example speaking assessment evaluation"""
    
    transcript = """
    Examiner: Tell me about your hometown.
    Candidate: I come from Mumbai, which is a very vibrant city in India. It's known for its diverse culture and bustling streets. I've lived there my entire life, and I really appreciate the energy and opportunities it offers.
    
    Examiner: What do you like most about living there?
    Candidate: What I like most is the diversity. You can find people from all walks of life, different cultures, different languages. It's like a melting pot of traditions. Plus, the food scene is amazing - you can get authentic cuisine from any part of India.
    
    [... rest of conversation ...]
    """
    
    result = await gemini_service.evaluate_speaking(
        transcript=transcript,
        assessment_type='academic_speaking',
        conversation_duration='12 minutes',
        assessment_id='test_speaking_001'
    )
    
    print(f"Overall Band: {result['overall_band']}")
    print(f"Fluency & Coherence: {result['fluency_coherence']['score']}")
    print(f"Feedback: {result['detailed_feedback']}")
    return result


# EXAMPLE 2: Evaluate Writing Assessment
async def example_writing_evaluation():
    """Example writing assessment evaluation"""
    
    essay = """
    Some people believe that university students should be required to attend classes. 
    Others believe that going to classes should be optional for students. 
    Which point of view do you agree with? Use specific reasons and details to explain your answer.
    
    In the modern educational landscape, the debate over mandatory class attendance has become 
    increasingly relevant. While some argue that attendance should be compulsory, I firmly believe 
    that university students should have the freedom to choose whether to attend classes.
    
    Firstly, university students are adults who should be responsible for their own learning...
    
    [... rest of essay ...]
    """
    
    result = await gemini_service.evaluate_writing(
        essay=essay,
        task_number=2,
        assessment_type='academic_writing',
        word_count=285,
        assessment_id='test_writing_002'
    )
    
    print(f"Overall Band: {result['overall_band']}")
    print(f"Task Response: {result['task_response']['score']}")
    print(f"Coherence & Cohesion: {result['coherence_cohesion']['score']}")
    print(f"Feedback: {result['detailed_feedback']}")
    return result


# EXAMPLE 3: Integration with Flask app.py route
"""
In your app.py, you would add something like this:

from gemini_ielts_service import gemini_service
import asyncio

@app.route('/api/evaluate-writing', methods=['POST'])
def evaluate_writing_route():
    data = request.get_json()
    
    # Extract essay details
    essay = data.get('essay')
    task_number = data.get('task_number', 2)
    assessment_type = data.get('assessment_type', 'academic_writing')
    word_count = len(essay.split())
    
    # Run async evaluation (Flask doesn't support async natively)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        gemini_service.evaluate_writing(
            essay=essay,
            task_number=task_number,
            assessment_type=assessment_type,
            word_count=word_count,
            assessment_id=f"user_{session.get('user_id')}_writing_{datetime.utcnow().timestamp()}"
        )
    )
    loop.close()
    
    return jsonify(result)

@app.route('/api/evaluate-speaking', methods=['POST'])
def evaluate_speaking_route():
    data = request.get_json()
    
    # Extract conversation details
    transcript = data.get('transcript')
    assessment_type = data.get('assessment_type', 'academic_speaking')
    duration = data.get('duration', '12 minutes')
    
    # Run async evaluation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        gemini_service.evaluate_speaking(
            transcript=transcript,
            assessment_type=assessment_type,
            conversation_duration=duration,
            assessment_id=f"user_{session.get('user_id')}_speaking_{datetime.utcnow().timestamp()}"
        )
    )
    loop.close()
    
    return jsonify(result)
"""


if __name__ == "__main__":
    # Run examples
    print("=" * 50)
    print("EXAMPLE 1: Speaking Assessment")
    print("=" * 50)
    asyncio.run(example_speaking_evaluation())
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Writing Assessment")
    print("=" * 50)
    asyncio.run(example_writing_evaluation())
