# 🚀 IELTS Assessment Workflow Optimization
## Adapting Eleven Labs Architecture for Flash-Lite Performance

---

## 🎯 Key Insight from Eleven Labs

Their **node-based workflow** with **dynamic LLM switching** is perfect for IELTS! We can use:
- **Different prompts** for each conversation phase
- **Progressive complexity** matching IELTS parts
- **Smart routing** based on response quality
- **Focused evaluation** at each node

This could make **Flash-Lite perform like Flash** at 82% less cost!

---

## 📊 Optimized IELTS Workflow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                IELTS SPEAKING WORKFLOW                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  START NODE (Initialization)                           │
│  ├─ System: Base IELTS examiner prompt                 │
│  ├─ Model: Flash-Lite                                  │
│  └─ Voice: Professional Maya                           │
│                      ↓                                  │
│  PART 1 SUBAGENT (Simple Q&A)                         │
│  ├─ Enhanced Prompt: Focus on basic accuracy          │
│  ├─ Model: Flash-Lite (sufficient for simple Q&A)     │
│  ├─ Duration: 4-5 minutes                             │
│  └─ Edge Condition: After 5 questions → Part 2        │
│                      ↓                                  │
│  EVALUATION NODE 1 (Quick Assessment)                  │
│  ├─ Tool: Basic scoring algorithm                      │
│  ├─ Decision: If score < 6.0 → Extra support          │
│  └─ Continue to Part 2                                │
│                      ↓                                  │
│  PART 2 SUBAGENT (Long Turn)                          │
│  ├─ Enhanced Prompt: Focus on coherence & fluency     │
│  ├─ Model: Flash-Lite with structured guidance        │
│  ├─ Duration: 3-4 minutes                             │
│  └─ Edge Condition: After 2 min speech → Part 3       │
│                      ↓                                  │
│  EVALUATION NODE 2 (Complexity Check)                  │
│  ├─ Tool: Complexity analyzer                          │
│  ├─ Decision: If complex → Switch to Flash for P3     │
│  └─ Otherwise continue with Flash-Lite                │
│                      ↓                                  │
│  PART 3 SUBAGENT (Abstract Discussion)                │
│  ├─ Enhanced Prompt: Deep analysis instructions       │
│  ├─ Model: Flash (if complexity high) OR Flash-Lite   │
│  ├─ Duration: 4-5 minutes                             │
│  └─ Edge Condition: Complete → Final evaluation       │
│                      ↓                                  │
│  FINAL EVALUATION NODE                                 │
│  ├─ Model: Nova Micro (text evaluation)               │
│  ├─ Generate comprehensive feedback                    │
│  └─ Return assessment results                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Enhanced Prompting Strategy (Eleven Labs-Inspired)

### **Base Agent Configuration**
```python
base_system_prompt = """
You are Maya, an IELTS examiner. Your role adapts based on the test phase.
Core responsibilities:
1. Maintain authentic IELTS test environment
2. Assess against official band descriptors
3. Provide natural, encouraging responses
4. Track specific evaluation criteria per phase
"""
```

### **Part 1 Subagent Override (Flash-Lite Optimized)**
```python
part1_override = """
PHASE: Part 1 - Introduction and Interview
FOCUS: Basic communication ability

EVALUATION PRIORITIES (for Flash-Lite efficiency):
1. Can the candidate communicate basic information? (Yes/No)
2. Are responses appropriate to questions? (Yes/No)
3. Is pronunciation generally clear? (Scale 1-5)
4. Grammar accuracy in simple sentences (Count errors)

SIMPLIFIED ASSESSMENT:
- Don't analyze complex structures (they won't use them yet)
- Focus on: clarity, appropriateness, basic fluency
- Track: hesitations, self-corrections, basic vocabulary

QUESTIONS TO ASK:
1. "Tell me about where you live"
2. "What do you do for work or study?"
3. "What do you enjoy doing in your free time?"
4. "How often do you use English?"
5. "What's your favorite type of food?"

RESPONSE PATTERN:
- Acknowledge answer briefly
- Ask follow-up if unclear
- Move to next question smoothly
"""
```

### **Part 2 Subagent Override (Flash-Lite with Structure)**
```python
part2_override = """
PHASE: Part 2 - Long Turn
FOCUS: Extended speaking ability

STRUCTURED EVALUATION (Flash-Lite optimization):
Track these specific markers:
□ Introduction (Did they start well?)
□ Main points (Count: ___ distinct ideas)
□ Examples given (Count: ___)
□ Conclusion (Did they summarize?)
□ Time management (Spoke for: ___ seconds)

COHERENCE CHECKLIST:
□ Used linking words (firstly, however, therefore)
□ Ideas flow logically
□ Stayed on topic

LEXICAL TRACKING:
□ Topic-specific vocabulary used: [list words]
□ Attempted complex words: [list attempts]
□ Repetitions noted: [list repeated words]

TOPIC CARD:
"Describe a memorable journey you have taken.
You should say:
- Where you went
- How you traveled
- Who you went with
- Why it was memorable"

SIMPLIFIED SCORING:
Instead of deep analysis, use pattern matching:
- 3+ linking words = Good coherence
- 5+ topic words = Good lexical resource
- 90+ seconds speaking = Good fluency
"""
```

### **Part 3 Subagent Override (Smart Model Selection)**
```python
part3_override = """
PHASE: Part 3 - Two-way Discussion
DYNAMIC MODEL SELECTION:

IF candidate showed Band 7+ indicators in Part 2:
  → USE Flash (complex assessment needed)
ELSE:
  → USE Flash-Lite (basic assessment sufficient)

COMPLEXITY INDICATORS (triggers Flash):
- Used subjunctive mood
- Expressed hypothetical situations
- Demonstrated abstract reasoning
- Used idiomatic expressions correctly

QUESTIONS (adapt based on level):
Basic (Flash-Lite):
1. "Why do people like to travel?"
2. "How has travel changed in recent years?"
3. "What are the benefits of travel?"

Advanced (Flash):
1. "How might virtual reality affect future tourism?"
2. "Should governments restrict travel for environmental reasons?"
3. "To what extent does travel broaden the mind?"

EVALUATION FOCUS:
Flash-Lite: Track basic argument structure
Flash: Analyze reasoning depth and linguistic complexity
"""
```

---

## 🔧 Implementation Code Updates

### **Updated Gemini Live Service with Workflow Support**

```python
class IELTSWorkflowManager:
    """
    Eleven Labs-inspired workflow manager for IELTS assessment
    Optimizes Flash-Lite to perform like Flash through smart prompting
    """
    
    def __init__(self, gemini_service: GeminiLiveService):
        self.gemini_service = gemini_service
        self.current_phase = "initialization"
        self.conversation_state = {
            'part1_responses': [],
            'part2_duration': 0,
            'part3_complexity': 'unknown',
            'evaluation_notes': {}
        }
        
    async def start_assessment(self, assessment_type: str = 'speaking'):
        """Initialize workflow with base configuration"""
        
        # Start with Flash-Lite (cost-optimized)
        self.model = 'gemini-2.5-flash-lite'
        
        # Base system prompt
        base_prompt = self.get_base_prompt(assessment_type)
        
        # Create initial session
        session = await self.gemini_service.start_maya_conversation(
            assessment_type=assessment_type,
            system_prompt=base_prompt,
            model=self.model
        )
        
        # Move to Part 1
        await self.transition_to_part1(session)
        return session
    
    async def transition_to_part1(self, session):
        """Transition to Part 1 with optimized prompting"""
        
        self.current_phase = 'part1'
        
        # Apply Part 1 subagent override
        part1_prompt = self.get_part1_optimized_prompt()
        await session.update_system_prompt(part1_prompt, append=True)
        
        # Track responses for evaluation
        session.on_response = lambda text: self.track_part1_response(text)
        
    async def evaluate_part1_completion(self, session):
        """Quick evaluation node after Part 1"""
        
        # Use simple pattern matching (Flash-Lite friendly)
        responses = self.conversation_state['part1_responses']
        
        basic_score = self.calculate_basic_score(responses)
        
        if basic_score < 6.0:
            # Provide extra support in Part 2
            await session.add_instruction(
                "Candidate needs encouragement. Be more supportive."
            )
        
        # Transition to Part 2
        await self.transition_to_part2(session)
        
    async def transition_to_part2(self, session):
        """Transition to Part 2 with structured evaluation"""
        
        self.current_phase = 'part2'
        
        # Apply Part 2 optimized prompt
        part2_prompt = self.get_part2_structured_prompt()
        await session.update_system_prompt(part2_prompt, append=True)
        
        # Start timer for duration tracking
        self.conversation_state['part2_start'] = datetime.utcnow()
        
    async def evaluate_complexity(self, transcript: str) -> str:
        """Determine if we need Flash for Part 3"""
        
        complexity_indicators = [
            'would have', 'could have', 'might have',  # Perfect modals
            'were I to', 'had I known',                 # Subjunctive
            'nevertheless', 'notwithstanding',          # Advanced connectors
            'hypothetically', 'theoretically'           # Abstract thinking
        ]
        
        complexity_score = sum(
            1 for indicator in complexity_indicators 
            if indicator in transcript.lower()
        )
        
        if complexity_score >= 3:
            self.conversation_state['part3_complexity'] = 'high'
            return 'gemini-2.5-flash'  # Switch to standard Flash
        else:
            self.conversation_state['part3_complexity'] = 'basic'
            return 'gemini-2.5-flash-lite'  # Stay with Flash-Lite
    
    async def transition_to_part3(self, session, transcript: str):
        """Smart transition to Part 3 with model selection"""
        
        self.current_phase = 'part3'
        
        # Determine optimal model based on complexity
        optimal_model = await self.evaluate_complexity(transcript)
        
        if optimal_model != self.model:
            # Switch models mid-conversation (Eleven Labs pattern)
            await session.switch_model(optimal_model)
            self.model = optimal_model
        
        # Apply Part 3 prompt (adapted to model capability)
        if optimal_model == 'gemini-2.5-flash':
            part3_prompt = self.get_part3_advanced_prompt()
        else:
            part3_prompt = self.get_part3_basic_prompt()
            
        await session.update_system_prompt(part3_prompt, append=True)
    
    def calculate_basic_score(self, responses: list) -> float:
        """
        Simplified scoring for Flash-Lite efficiency
        Uses pattern matching instead of deep analysis
        """
        score = 5.0  # Base score
        
        for response in responses:
            # Simple heuristics
            if len(response.split()) > 20:
                score += 0.2  # Good length
            if any(word in response.lower() for word in ['because', 'although', 'however']):
                score += 0.1  # Uses connectors
            if response.count(',') > 1:
                score += 0.1  # Complex sentences
                
        return min(score, 9.0)
    
    def get_part1_optimized_prompt(self) -> str:
        """Get optimized Part 1 prompt for Flash-Lite"""
        return """
        SIMPLIFIED EVALUATION MODE - PART 1
        
        Focus on these 5 key indicators only:
        1. Answers the question (Yes/No)
        2. Provides some detail (Yes/No)  
        3. Speech is continuous (Yes/No)
        4. Vocabulary is appropriate (Yes/No)
        5. Grammar is accurate in simple sentences (Yes/No)
        
        DO NOT analyze complex patterns. 
        DO NOT evaluate sophisticated structures.
        Just track the 5 indicators above.
        
        Ask 5 simple questions about daily life.
        Keep interactions brief and natural.
        """
    
    def get_part2_structured_prompt(self) -> str:
        """Structured Part 2 prompt for Flash-Lite efficiency"""
        return """
        STRUCTURED EVALUATION MODE - PART 2
        
        Use this checklist format:
        
        FLUENCY MARKERS:
        □ Spoke for 60+ seconds
        □ Less than 3 long pauses
        □ Self-corrections don't disrupt flow
        
        COHERENCE MARKERS:
        □ Clear introduction
        □ 2-3 main points
        □ Examples provided
        □ Logical sequence
        
        VOCABULARY MARKERS:
        □ 5+ topic-specific words
        □ Attempted paraphrase
        □ No excessive repetition
        
        GRAMMAR MARKERS:
        □ Past tense used correctly
        □ Complex sentences attempted
        □ Few basic errors
        
        Simply check boxes, don't analyze deeply.
        This structured approach helps Flash-Lite be more accurate.
        """
```

---

## 📊 Cost & Quality Impact

### **Traditional Approach**
- All Standard Flash: $588/10K assessments
- Quality: High
- Issue: Expensive

### **Basic Flash-Lite**
- All Flash-Lite: $105/10K assessments
- Quality: Medium
- Issue: May miss nuances

### **Workflow-Optimized Flash-Lite** ✨
- Smart prompting + conditional routing: ~$150/10K assessments
- Quality: **Near-Flash level** (through structured evaluation)
- Savings: **$438/month (74%)**

---

## 🎯 Implementation Steps

1. **Update System Prompts**
   - Replace generic prompts with phase-specific ones
   - Add structured evaluation checklists
   - Include pattern-matching rules

2. **Add Workflow Manager**
   - Implement `IELTSWorkflowManager` class
   - Handle phase transitions
   - Track conversation state

3. **Implement Smart Routing**
   - Complexity detection after Part 2
   - Conditional model switching
   - Adaptive questioning based on level

4. **Test Quality**
   - Compare scores: Optimized Flash-Lite vs Standard Flash
   - Verify checklist approach maintains accuracy
   - Measure cost savings

---

## ✅ Expected Outcomes

**With Eleven Labs-inspired optimization:**
- **Flash-Lite quality:** 85-90% of Flash performance
- **Cost reduction:** 74% savings
- **Better structure:** More consistent assessments
- **Flexibility:** Can upgrade specific parts if needed

**Key Innovation:**
Instead of relying on the model's general intelligence, we **guide it with structure** - making Flash-Lite much more effective through:
- Phase-specific prompts
- Checklist-based evaluation  
- Pattern matching instead of deep analysis
- Smart routing when complexity is needed

This approach essentially **teaches Flash-Lite to be a better IELTS examiner** rather than hoping it figures it out on its own!

---

## 🚀 Next Steps

1. **Implement workflow manager** in `gemini_live_audio_service.py`
2. **Update prompts** with structured evaluation
3. **Add complexity detection** for smart routing
4. **Test with real assessments** to verify quality
5. **Monitor cost savings** in production

This could achieve **near-Flash quality at Flash-Lite prices**! 🎉