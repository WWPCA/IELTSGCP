"""Quick validation that Gemini service is properly configured"""
import os
import sys

print("🔍 Gemini Service Validation")
print("=" * 60)

# Check 1: API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
else:
    print("❌ GEMINI_API_KEY not found!")
    sys.exit(1)

# Check 2: Import service
try:
    from gemini_ielts_service import gemini_service, GeminiIELTSService
    print("✅ gemini_ielts_service imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Check 3: Service initialization
try:
    service = GeminiIELTSService()
    print(f"✅ Service initialized with model: {service.model}")
except Exception as e:
    print(f"❌ Service initialization failed: {e}")
    sys.exit(1)

# Check 4: Import rubrics
try:
    from assessment_criteria.speaking_criteria import SPEAKING_BAND_DESCRIPTORS
    from assessment_criteria.writing_criteria import WRITING_TASK2_BAND_DESCRIPTORS
    print(f"✅ IELTS rubrics loaded ({len(SPEAKING_BAND_DESCRIPTORS)} speaking bands)")
except Exception as e:
    print(f"❌ Rubrics import failed: {e}")
    sys.exit(1)

# Check 5: Prompt building
try:
    prompt = service._build_writing_prompt(
        essay="This is a test essay about technology.",
        task_number=2,
        assessment_type='academic_writing'
    )
    print(f"✅ Prompt generation works (length: {len(prompt)} chars)")
    # print("\n📝 Sample Prompt Preview:")
    # print(prompt[:500] + "...")
except Exception as e:
    print(f"❌ Prompt generation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 All validation checks passed!")
print("=" * 60)
print("\n📋 Summary:")
print("  • Gemini API key configured")
print("  • Service module imports correctly")
print("  • IELTS rubrics available")
print("  • Prompt generation functional")
print("\n✨ The service is ready for assessment evaluations!")
print("\nNote: Actual Gemini API calls may take 5-15 seconds depending on essay length.")
