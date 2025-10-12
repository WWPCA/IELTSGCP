# Full Mock Test Data Requirements

## Overview
Your full mock test templates are ready! Here's what you need to provide to populate them.

---

## ✅ What You Already Have
- **Writing Tasks**: Gemini AI handles evaluation automatically (no database needed)
- **Speaking Tests**: Gemini Live API (Maya) conducts interviews (no database needed)

---

## 📋 What You Need to Provide

### 1. LISTENING SECTION (Same for Academic & General)

**Audio Files Required:**
- `listening_part1.mp3` - Everyday social conversation (2 speakers, ~5 min)
- `listening_part2.mp3` - Monologue in everyday context (~5 min)
- `listening_part3.mp3` - Educational/training conversation (up to 4 speakers, ~5 min)
- `listening_part4.mp3` - Academic lecture/monologue (~5 min)

**Question Database Required:**
```json
{
  "part_1_questions": [
    {
      "question_number": 1,
      "question_type": "form_completion",
      "question_text": "Name: ________",
      "correct_answer": "Sarah Jones",
      "audio_timestamp": "0:15-0:20"
    }
    // ... 9 more questions (Q1-10)
  ],
  "part_2_questions": [ /* Q11-20 */ ],
  "part_3_questions": [ /* Q21-30 */ ],
  "part_4_questions": [ /* Q31-40 */ ]
}
```

**Question Types to Include:**
- Form completion
- Multiple choice
- Matching
- Note completion
- Labeling diagrams
- Sentence completion
- Summary completion

---

### 2. READING SECTION - ACADEMIC

**Passages Required:**
- `academic_passage_1.txt` (700-900 words, easier difficulty)
  - Topic: Science, technology, nature, or society
  - Source-style: Journal/magazine article
  
- `academic_passage_2.txt` (700-900 words, moderate difficulty)
  - Topic: Education, environment, business, culture
  - Source-style: Academic book/research
  
- `academic_passage_3.txt` (750-950 words, harder difficulty)
  - Topic: Complex research/theory
  - Source-style: Academic journal

**Question Database Required:**
```json
{
  "passage_1_questions": [
    {
      "question_number": 1,
      "question_type": "true_false_not_given",
      "statement": "The research was conducted over three years.",
      "correct_answer": "TRUE",
      "explanation": "Paragraph 2 states..."
    }
    // ... 12 more questions (Q1-13)
  ],
  "passage_2_questions": [ /* Q14-26 */ ],
  "passage_3_questions": [ /* Q27-40 */ ]
}
```

**Question Types:**
- True/False/Not Given
- Yes/No/Not Given
- Multiple choice
- Matching headings
- Matching information
- Matching features
- Sentence completion
- Summary completion
- Note completion

---

### 3. READING SECTION - GENERAL TRAINING

**Texts Required:**

**Section 1 - Social Survival (2-3 short texts, 600-900 words total):**
- Notices, advertisements, timetables
- Example: Hotel notice + Train timetable + Activity schedule

**Section 2 - Workplace Survival (2 texts, 600-900 words total):**
- Job descriptions, contracts, training materials
- Example: Job posting + Staff handbook excerpt

**Section 3 - General Reading (1 longer text, 750-950 words):**
- Newspaper/magazine article on general interest topic
- Example: Article about modern education or technology trends

**Question Database Required:**
```json
{
  "section_1_questions": [ /* Q1-14 */ ],
  "section_2_questions": [ /* Q15-27 */ ],
  "section_3_questions": [ /* Q28-40 */ ]
}
```

---

## 📊 Summary Table

| Section | Audio Files | Text Files | Questions | AI-Generated |
|---------|-------------|------------|-----------|--------------|
| Listening | ✅ 4 files needed | - | ✅ 40 Q's needed | - |
| Reading (Academic) | - | ✅ 3 passages needed | ✅ 40 Q's needed | - |
| Reading (General) | - | ✅ 6-7 texts needed | ✅ 40 Q's needed | - |
| Writing | - | - | - | ✅ Gemini AI |
| Speaking | - | - | - | ✅ Gemini Live |

---

## 🎯 File Format Examples

### Listening Question JSON:
```json
{
  "question_number": 15,
  "question_type": "multiple_choice",
  "question_text": "What is the main purpose of the facility?",
  "options": {
    "A": "Entertainment",
    "B": "Education",
    "C": "Research",
    "D": "Conservation"
  },
  "correct_answer": "B",
  "audio_timestamp": "5:30-5:45",
  "marks": 1
}
```

### Reading Question JSON:
```json
{
  "question_number": 20,
  "question_type": "sentence_completion",
  "instruction": "Complete the sentence using NO MORE THAN THREE WORDS from the passage.",
  "question_text": "The experiment showed that ________ was the primary factor.",
  "correct_answer": "water temperature",
  "paragraph_reference": 4,
  "marks": 1
}
```

---

## 🚀 Next Steps

**Once you provide these files:**
1. I'll populate the templates with your data
2. Create database entries in Firestore
3. Link audio files to Cloud Storage
4. Test the complete workflow end-to-end
5. Deploy to test.ieltsaiprep.com

**Current Status:**
- ✅ Templates created and ready
- ✅ Gemini endpoints added for Writing and Speaking
- ⏳ Awaiting Listening audio files + questions
- ⏳ Awaiting Reading passages + questions

---

## 💰 Pricing Summary (Updated)

| Product | Price | Assessments Included |
|---------|-------|---------------------|
| Academic/General Writing | $25 | 2 assessments |
| Academic/General Speaking | $25 | 2 assessments |
| **Full Mock Test** | **$99** | **2 complete tests** (all 4 sections) |

**GCP Cost Savings:**
- Base: $43-49/month (minimal traffic)
- Moderate usage: ~$173/month
- **54% cheaper than AWS ($375/month)**
- **Savings: $202/month**
