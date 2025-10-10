"""
Quick test script for Gemini IELTS Service
Run this to verify Gemini integration works correctly
"""
import asyncio
import json
from gemini_ielts_service import gemini_service

async def test_writing_assessment():
    """Test writing assessment with a sample essay"""
    print("🧪 Testing Gemini Writing Assessment...")
    print("-" * 60)
    
    sample_essay = """
Some people believe that university students should be required to attend classes. 
Others believe that going to classes should be optional for students. 
Which point of view do you agree with?

In the contemporary academic environment, the question of mandatory class attendance 
has generated considerable debate. While some advocate for compulsory attendance, 
I firmly contend that university students should possess the autonomy to determine 
their class participation.

Firstly, university students are mature individuals capable of managing their own 
educational journey. Unlike younger pupils who require structured guidance, adult 
learners have developed the critical thinking skills necessary to identify their 
learning needs. When students are granted the freedom to choose, they tend to 
engage more meaningfully with the material, as attendance becomes a conscious 
decision rather than a forced obligation.

Moreover, the digital age has transformed educational accessibility. With the 
proliferation of online resources, recorded lectures, and digital libraries, 
students can access course materials regardless of physical attendance. A student 
who cannot attend due to work commitments or health issues should not be penalized 
when alternative learning methods exist.

In conclusion, while attendance policies may serve administrative purposes, they 
fail to acknowledge the maturity and diverse circumstances of university students. 
Optional attendance promotes responsibility and accommodates the varied needs of 
modern learners.
"""
    
    try:
        result = await gemini_service.evaluate_writing(
            essay=sample_essay,
            task_number=2,
            assessment_type='academic_writing',
            word_count=len(sample_essay.split()),
            assessment_id='test_001'
        )
        
        print("✅ Assessment completed successfully!\n")
        print(f"📊 Overall Band Score: {result['overall_band']}")
        print(f"📝 Word Count: {result['word_count']}")
        print(f"\n📋 Detailed Scores:")
        print(f"  • Task Response: {result['task_response']['score']}")
        print(f"  • Coherence & Cohesion: {result['coherence_cohesion']['score']}")
        print(f"  • Lexical Resource: {result['lexical_resource']['score']}")
        print(f"  • Grammatical Range: {result['grammatical_range']['score']}")
        
        print(f"\n💭 Overall Feedback:")
        print(f"{result['detailed_feedback']}")
        
        print(f"\n✨ Strengths:")
        for strength in result['task_response']['strengths']:
            print(f"  • {strength}")
        
        print(f"\n📈 Areas for Improvement:")
        for improvement in result['task_response']['improvements']:
            print(f"  • {improvement}")
        
        print("\n" + "=" * 60)
        print("🎉 Full JSON Response:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"❌ Error during assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_speaking_assessment():
    """Test speaking assessment with a sample transcript"""
    print("\n🧪 Testing Gemini Speaking Assessment...")
    print("-" * 60)
    
    sample_transcript = """
Examiner: Good morning. My name is Sarah. Can you tell me your full name, please?
Candidate: Good morning. My name is Raj Patel.

Examiner: Thank you. Now, let's talk about your hometown. Where are you from?
Candidate: I'm from Mumbai, which is located on the west coast of India. It's one of the most populous cities in the world and serves as the financial capital of the country.

Examiner: What do you like most about living there?
Candidate: What I particularly appreciate about Mumbai is its incredible diversity. You can encounter people from virtually every corner of India, speaking different languages and practicing various traditions. The city never sleeps - there's always something happening, whether it's cultural festivals, music concerts, or just the bustling street life. Additionally, the professional opportunities are abundant, especially in finance and entertainment industries.

Examiner: How has your hometown changed over the years?
Candidate: Well, the transformation has been quite remarkable. When I was growing up, the infrastructure was considerably less developed. Now we have modern metro systems, improved roads, and better connectivity. However, this rapid development has also brought challenges - traffic congestion has worsened, and housing has become increasingly expensive. The skyline keeps changing with new skyscrapers, but I sometimes miss the old charm of the neighborhood shops and traditional markets that are gradually disappearing.

Examiner: That's interesting. Now I'd like you to describe a memorable journey you've taken...
"""
    
    try:
        result = await gemini_service.evaluate_speaking(
            transcript=sample_transcript,
            assessment_type='academic_speaking',
            conversation_duration='12 minutes',
            assessment_id='test_speaking_001'
        )
        
        print("✅ Assessment completed successfully!\n")
        print(f"📊 Overall Band Score: {result['overall_band']}")
        print(f"⏱️ Duration: {result['conversation_duration']}")
        print(f"\n📋 Detailed Scores:")
        print(f"  • Fluency & Coherence: {result['fluency_coherence']['score']}")
        print(f"  • Lexical Resource: {result['lexical_resource']['score']}")
        print(f"  • Grammatical Range: {result['grammatical_range']['score']}")
        print(f"  • Pronunciation: {result['pronunciation']['score']}")
        
        print(f"\n💭 Overall Feedback:")
        print(f"{result['detailed_feedback']}")
        
        print("\n" + "=" * 60)
        print("🎉 Full JSON Response:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"❌ Error during assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🚀 GEMINI IELTS SERVICE TEST SUITE")
    print("=" * 60)
    
    # Test 1: Writing Assessment
    writing_result = await test_writing_assessment()
    
    # Test 2: Speaking Assessment
    speaking_result = await test_speaking_assessment()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    if writing_result:
        print(f"✅ Writing Test: PASSED (Band {writing_result['overall_band']})")
    else:
        print("❌ Writing Test: FAILED")
    
    if speaking_result:
        print(f"✅ Speaking Test: PASSED (Band {speaking_result['overall_band']})")
    else:
        print("❌ Speaking Test: FAILED")
    
    print("\n🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())
