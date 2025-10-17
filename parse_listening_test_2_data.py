"""
Parser for IELTS Academic Listening Test 2
Extracts questions and answers from test document
"""
from typing import Dict, List, Any

class ListeningTest2Parser:
    """Parse Academic Listening Test 2 questions and answers"""
    
    def parse_academic_test_2(self) -> Dict[str, Any]:
        """
        Parse Academic Listening Test 2 specifically
        """
        
        # Test metadata
        test_data = {
            'test_id': 'academic-listening-test-2',
            'test_type': 'academic',
            'test_number': 2,
            'title': 'IELTS Academic Listening Test 2',
            'total_questions': 40,
            'duration_minutes': 30,
            'sections': [
                {
                    'number': 1,
                    'title': 'Library Registration',
                    'description': 'Conversation between a student and a librarian',
                    'question_range': '1-10',
                    'audio_file': 'Academic_Listening_Test_2_Section_1.mp3'
                },
                {
                    'number': 2,
                    'title': 'National Science Museum Tour',
                    'description': 'Tour guide describing the museum',
                    'question_range': '11-20',
                    'audio_file': 'Academic_Listening_Test_2_Section_2.mp3'
                },
                {
                    'number': 3,
                    'title': 'Psychology Research Project',
                    'description': 'Two students discussing their research',
                    'question_range': '21-30',
                    'audio_file': 'Academic_Listening_Test_2_Section_3.mp3'
                },
                {
                    'number': 4,
                    'title': 'Water Conservation Strategies',
                    'description': 'Lecture about urban water conservation',
                    'question_range': '31-40',
                    'audio_file': 'Academic_Listening_Test_2_Section_4.mp3'
                }
            ]
        }
        
        # Parse questions
        questions = []
        
        # Section 1: Questions 1-10 (Library Registration)
        # Form completion (1-5)
        questions.extend([
            {
                'number': 1,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Complete the form. Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': 'Full Name: Sarah __________________',
                'context': 'LIBRARY REGISTRATION FORM'
            },
            {
                'number': 2,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': 'Date of Birth: __________________ 1998',
                'context': 'LIBRARY REGISTRATION FORM'
            },
            {
                'number': 3,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': 'Student ID: __________________',
                'context': 'LIBRARY REGISTRATION FORM'
            },
            {
                'number': 4,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': 'Contact Number: __________________',
                'context': 'LIBRARY REGISTRATION FORM'
            },
            {
                'number': 5,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': 'Email: __________________ @university.edu',
                'context': 'LIBRARY REGISTRATION FORM'
            }
        ])
        
        # Multiple choice (6-10)
        questions.extend([
            {
                'number': 6,
                'section': 1,
                'type': 'multiple_choice',
                'text': 'How many books can students borrow at one time?',
                'options': ['A. 5 books', 'B. 10 books', 'C. 15 books']
            },
            {
                'number': 7,
                'section': 1,
                'type': 'multiple_choice',
                'text': 'How long is the standard loan period?',
                'options': ['A. 2 weeks', 'B. 3 weeks', 'C. 4 weeks']
            },
            {
                'number': 8,
                'section': 1,
                'type': 'multiple_choice',
                'text': 'What happens if a book is overdue?',
                'options': ['A. A fine of 50p per day', 'B. A fine of £1 per day', 'C. Borrowing privileges are suspended']
            },
            {
                'number': 9,
                'section': 1,
                'type': 'multiple_choice',
                'text': 'Which resource is NOT available online?',
                'options': ['A. Journal articles', 'B. Video tutorials', 'C. Physical archives']
            },
            {
                'number': 10,
                'section': 1,
                'type': 'multiple_choice',
                'text': 'When is the library open until 10 PM?',
                'options': ['A. Monday to Friday', 'B. Monday to Thursday', 'C. Every day']
            }
        ])
        
        # Section 2: Questions 11-20 (Museum Tour)
        # Multiple choice (11-15)
        questions.extend([
            {
                'number': 11,
                'section': 2,
                'type': 'multiple_choice',
                'text': 'The museum was originally opened in',
                'options': ['A. 1857', 'B. 1887', 'C. 1927']
            },
            {
                'number': 12,
                'section': 2,
                'type': 'multiple_choice',
                'text': 'The Space Exploration gallery features',
                'options': ['A. a real moon rock', 'B. a flight simulator', 'C. both of the above']
            },
            {
                'number': 13,
                'section': 2,
                'type': 'multiple_choice',
                'text': 'Interactive exhibits are particularly designed for',
                'options': ['A. university students', 'B. children under 12', 'C. all ages']
            },
            {
                'number': 14,
                'section': 2,
                'type': 'multiple_choice',
                'text': 'The museum café is located on the',
                'options': ['A. ground floor', 'B. second floor', 'C. third floor']
            },
            {
                'number': 15,
                'section': 2,
                'type': 'multiple_choice',
                'text': 'Special exhibitions change every',
                'options': ['A. three months', 'B. six months', 'C. twelve months']
            }
        ])
        
        # Map labeling (16-20)
        for i in range(16, 21):
            questions.append({
                'number': i,
                'section': 2,
                'type': 'map_labeling',
                'instructions': 'Label the museum floor plan. Write the correct letter, A-H',
                'text': self.get_map_question_text(i),
                'options': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            })
        
        # Section 3: Questions 21-30 (Research Discussion)
        # Matching (21-25)
        for i in range(21, 26):
            questions.append({
                'number': i,
                'section': 3,
                'type': 'matching',
                'instructions': 'What decision do the speakers make? Write the correct letter, A-F',
                'text': self.get_research_aspect(i),
                'options': [
                    'A. Already decided',
                    'B. Needs further research', 
                    'C. Will be randomized',
                    'D. Depends on budget',
                    'E. Must be approved by ethics committee',
                    'F. Will use self-reporting'
                ]
            })
        
        # Multiple choice (26-30)
        questions.extend([
            {
                'number': 26,
                'section': 3,
                'type': 'multiple_choice',
                'text': 'How many experimental groups will the study have?',
                'options': ['A. Two groups', 'B. Three groups', 'C. Four groups']
            },
            {
                'number': 27,
                'section': 3,
                'type': 'multiple_choice',
                'text': 'Tom suggests limiting sleep deprivation to',
                'options': ['A. one night', 'B. two nights', 'C. three nights']
            },
            {
                'number': 28,
                'section': 3,
                'type': 'multiple_choice',
                'text': 'The memory tests should be conducted',
                'options': [
                    'A. in the evening',
                    'B. at different times for different participants',
                    'C. in the morning at the same time'
                ]
            },
            {
                'number': 29,
                'section': 3,
                'type': 'multiple_choice',
                'text': 'What statistical test do they plan to use?',
                'options': ['A. T-test', 'B. ANOVA', 'C. Chi-square']
            },
            {
                'number': 30,
                'section': 3,
                'type': 'multiple_choice',
                'text': 'They plan to meet again to work on the ethics application',
                'options': ['A. this weekend', 'B. on Monday', 'C. on Tuesday']
            }
        ])
        
        # Section 4: Questions 31-40 (Water Conservation)
        # Sentence completion (31-34)
        questions.extend([
            {
                'number': 31,
                'section': 4,
                'type': 'sentence_completion',
                'instructions': 'Complete the sentences. Write NO MORE THAN TWO WORDS',
                'text': 'Urban areas consume approximately __________________ of the world\'s freshwater supply.'
            },
            {
                'number': 32,
                'section': 4,
                'type': 'sentence_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS',
                'text': 'Rainwater harvesting systems can reduce household water usage by up to __________________.'
            },
            {
                'number': 33,
                'section': 4,
                'type': 'sentence_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS',
                'text': 'Grey water refers to water from sinks, showers, and __________________.'
            },
            {
                'number': 34,
                'section': 4,
                'type': 'sentence_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS',
                'text': 'Smart irrigation systems use __________________ to determine when watering is needed.'
            }
        ])
        
        # Table completion (35-40)
        for i in range(35, 41):
            questions.append({
                'number': i,
                'section': 4,
                'type': 'table_completion',
                'instructions': 'Complete the table. Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'text': self.get_table_question(i)
            })
        
        # Answer key
        answers = {
            '1': 'Henderson',
            '2': '15th March',  # Also accepts: 15 March, March 15
            '3': 'LB47293',
            '4': '07892 445 621',
            '5': 's.henderson',
            '6': 'B',
            '7': 'B',
            '8': 'A',
            '9': 'C',
            '10': 'B',
            '11': 'B',  # 1887
            '12': 'C',  # both
            '13': 'C',  # all ages
            '14': 'B',  # second floor
            '15': 'B',  # six months
            '16': 'B',
            '17': 'E',
            '18': 'G',
            '19': 'A',
            '20': 'F',
            '21': 'A',  # Already decided
            '22': 'A',  # Already decided
            '23': 'C',  # Will be randomized
            '24': 'F',  # Will use self-reporting
            '25': 'A',  # Already decided
            '26': 'B',  # Three groups
            '27': 'A',  # one night
            '28': 'C',  # morning at same time
            '29': 'B',  # ANOVA
            '30': 'C',  # Tuesday
            '31': 'three-quarters',  # Also accepts: 75%
            '32': '40%',  # Also accepts: forty percent
            '33': 'washing machines',
            '34': 'sensors',  # Also accepts: soil moisture
            '35': '£50-150',  # Also accepts: Low
            '36': '£2,000-5,000',  # Also accepts: High
            '37': 'two weeks',  # Also accepts: 2 weeks
            '38': '50-70%',  # Also accepts: 50-70 percent
            '39': '2-3 months',  # Also accepts: two to three months
            '40': 'Varies'
        }
        
        # Acceptable answer variations (for validation)
        answer_variations = {
            '2': ['15th March', '15 March', 'March 15', '15/03', '15/3'],
            '31': ['three-quarters', '75%', '75 percent', 'three quarters'],
            '32': ['40%', 'forty percent', '40 percent'],
            '34': ['sensors', 'soil moisture', 'moisture sensors'],
            '35': ['£50-150', 'Low', '50-150'],
            '36': ['£2,000-5,000', 'High', '2000-5000'],
            '37': ['two weeks', '2 weeks', '14 days'],
            '38': ['50-70%', '50-70 percent', '50 to 70 percent'],
            '39': ['2-3 months', 'two to three months', '2 to 3 months']
        }
        
        return {
            'test_data': test_data,
            'questions': questions,
            'answers': answers,
            'answer_variations': answer_variations
        }
    
    def get_map_question_text(self, num: int) -> str:
        """Get map labeling question text"""
        map_items = {
            16: 'Energy and Power Gallery',
            17: 'Medical Innovations Gallery',
            18: 'Gift Shop',
            19: 'Information Desk',
            20: 'Temporary Exhibition Space'
        }
        return map_items.get(num, '')
    
    def get_research_aspect(self, num: int) -> str:
        """Get research aspect for matching questions"""
        aspects = {
            21: 'Research methodology',
            22: 'Number of participants',
            23: 'Order of memory tests',
            24: 'Sleep measurement method',
            25: 'Participant compensation'
        }
        return aspects.get(num, '')
    
    def get_table_question(self, num: int) -> str:
        """Get table completion question"""
        table_items = {
            35: 'Installation cost for basic rainwater system',
            36: 'Installation cost for advanced grey water system',
            37: 'Typical installation time',
            38: 'Water saving percentage for irrigation systems',
            39: 'Payback period',
            40: 'Maintenance requirements'
        }
        return table_items.get(num, '')