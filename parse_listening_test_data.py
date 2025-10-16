"""
Parser for IELTS Listening Test Data
Extracts questions, answers, and metadata from test documents
"""
import re
from typing import Dict, List, Tuple, Any

class ListeningTestParser:
    """Parse listening test questions and answers from document"""
    
    def __init__(self):
        self.sections = []
        self.questions = []
        self.answers = {}
        self.test_metadata = {}
    
    def parse_academic_test_1(self) -> Dict[str, Any]:
        """
        Parse Academic Listening Test 1 specifically
        Based on the provided document structure
        """
        
        # Test metadata
        test_data = {
            'test_id': 'academic-listening-test-1',
            'test_type': 'academic',
            'test_number': 1,
            'title': 'IELTS Academic Listening Test 1',
            'sections': [
                {
                    'number': 1,
                    'title': 'Student Accommodation Request',
                    'audio_filename': 'IELTS_Academic_Listening_Test_1_Section_1_Student_Accommodation_Request.mp3',
                    'question_range': '1-10',
                    'question_count': 10,
                    'description': 'Conversation between a student and a housing officer'
                },
                {
                    'number': 2,
                    'title': 'Bellingham Castle Tour',
                    'audio_filename': 'Academic_Listening_Test_1_Section_2_Bellingham_Castle_Tour.mp3',
                    'question_range': '11-20',
                    'question_count': 10,
                    'visual_aid': 'section2_castle_map.png',
                    'description': 'Tour guide giving information about a historic castle'
                },
                {
                    'number': 3,
                    'title': 'Renewable Energy Research Project',
                    'audio_filename': 'Academic_Listening_Test_1_Section_3_Renewable_Energy_Research_Project.mp3',
                    'question_range': '21-30',
                    'question_count': 10,
                    'description': 'Two students discussing their research project'
                },
                {
                    'number': 4,
                    'title': 'Social Media and Mental Health',
                    'audio_filename': 'Academic_Listening_Test_1_Section_4_Lecture.mp3',
                    'question_range': '31-40',
                    'question_count': 10,
                    'description': 'Lecture about the impact of social media on mental health'
                }
            ]
        }
        
        # Parse questions
        questions = []
        
        # Section 1: Questions 1-10
        # Questions 1-5: Form completion
        for i in range(1, 6):
            questions.append({
                'number': i,
                'section': 1,
                'type': 'form_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'max_words': 2,
                'text': self.get_section1_question_text(i)
            })
        
        # Questions 6-10: Multiple choice
        for i in range(6, 11):
            questions.append({
                'number': i,
                'section': 1,
                'type': 'multiple_choice',
                'text': self.get_section1_mc_question(i),
                'options': ['A', 'B', 'C']
            })
        
        # Section 2: Questions 11-20
        # Questions 11-14: Multiple choice
        for i in range(11, 15):
            questions.append({
                'number': i,
                'section': 2,
                'type': 'multiple_choice',
                'text': self.get_section2_mc_question(i),
                'options': ['A', 'B', 'C']
            })
        
        # Questions 15-20: Map labeling
        for i in range(15, 21):
            questions.append({
                'number': i,
                'section': 2,
                'type': 'map_labeling',
                'text': self.get_section2_map_question(i),
                'options': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                'requires_visual': True
            })
        
        # Section 3: Questions 21-30
        # Questions 21-24: Multiple choice
        for i in range(21, 25):
            questions.append({
                'number': i,
                'section': 3,
                'type': 'multiple_choice',
                'text': self.get_section3_mc_question(i),
                'options': ['A', 'B', 'C']
            })
        
        # Questions 25-30: Matching opinions
        for i in range(25, 31):
            questions.append({
                'number': i,
                'section': 3,
                'type': 'matching',
                'text': self.get_section3_matching_question(i),
                'options': ['A', 'B', 'C'],
                'option_descriptions': {
                    'A': 'Most promising for future development',
                    'B': 'Currently too expensive to implement',
                    'C': 'Has significant environmental drawbacks'
                }
            })
        
        # Section 4: Questions 31-40
        # Questions 31-34: Sentence completion
        for i in range(31, 35):
            questions.append({
                'number': i,
                'section': 4,
                'type': 'sentence_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS',
                'max_words': 2,
                'text': self.get_section4_sentence(i)
            })
        
        # Questions 35-40: Note completion
        for i in range(35, 41):
            questions.append({
                'number': i,
                'section': 4,
                'type': 'note_completion',
                'instructions': 'Write NO MORE THAN TWO WORDS AND/OR A NUMBER',
                'max_words': 2,
                'text': self.get_section4_note(i)
            })
        
        # Answer key
        answers = {
            '1': 'SM47892',
            '2': 'South',
            '3': '180',
            '4': '15th/15',
            '5': 'ground',
            '6': 'C',
            '7': 'A',
            '8': 'C',
            '9': 'C',
            '10': 'B',
            '11': 'B',
            '12': 'B',
            '13': 'B',
            '14': 'C',
            '15': 'D',
            '16': 'F',
            '17': 'B',
            '18': 'H',
            '19': 'E',
            '20': 'A',
            '21': 'B',
            '22': 'B',
            '23': 'B',
            '24': 'A',
            '25': 'A',
            '26': 'C',
            '27': 'B',
            '28': 'B',
            '29': 'A',
            '30': 'B',
            '31': 'attention',
            '32': 'depression',
            '33': 'inadequacy',
            '34': 'social support',
            '35': 'three/3',
            '36': 'younger',
            '37': 'one-week break/week break/one week',
            '38': 'sleep quality',
            '39': 'time limits',
            '40': 'face-to-face'
        }
        
        return {
            'test_data': test_data,
            'questions': questions,
            'answers': answers
        }
    
    def get_section1_question_text(self, num: int) -> str:
        """Get question text for Section 1 form completion"""
        texts = {
            1: "Student ID",
            2: "Preferred location (which campus)",
            3: "Maximum weekly rent (£)",
            4: "Move-in date (day in September)",
            5: "Special requirement (which floor)"
        }
        return texts.get(num, "")
    
    def get_section1_mc_question(self, num: int) -> str:
        """Get multiple choice question for Section 1"""
        questions = {
            6: "What is included in the rent?",
            7: "How many people will Sarah share with?",
            8: "What does Sarah need to pay as a deposit?",
            9: "The accommodation contract is for",
            10: "Sarah can collect her keys from"
        }
        return questions.get(num, "")
    
    def get_section2_mc_question(self, num: int) -> str:
        """Get multiple choice question for Section 2"""
        questions = {
            11: "Bellingham Castle was originally built in",
            12: "The castle was constructed primarily to",
            13: "What happened to the castle in the 17th century?",
            14: "The Great Hall is famous for its"
        }
        return questions.get(num, "")
    
    def get_section2_map_question(self, num: int) -> str:
        """Get map labeling question for Section 2"""
        locations = {
            15: "Gift Shop",
            16: "Tea Room",
            17: "Chapel",
            18: "Garden",
            19: "Armory",
            20: "Dungeon"
        }
        return locations.get(num, "")
    
    def get_section3_mc_question(self, num: int) -> str:
        """Get multiple choice question for Section 3"""
        questions = {
            21: "What aspect of renewable energy will their project focus on?",
            22: "Mark suggests they should",
            23: "Jennifer is concerned about",
            24: "Their tutor recommended they"
        }
        return questions.get(num, "")
    
    def get_section3_matching_question(self, num: int) -> str:
        """Get matching question for Section 3"""
        energy_sources = {
            25: "Solar power (Mark)",
            26: "Wind energy (Jennifer)",
            27: "Hydroelectric (Mark)",
            28: "Biomass (Jennifer)",
            29: "Geothermal (Mark)",
            30: "Tidal power (Jennifer)"
        }
        return energy_sources.get(num, "")
    
    def get_section4_sentence(self, num: int) -> str:
        """Get sentence completion for Section 4"""
        sentences = {
            31: "Social media platforms are designed to maximize user _____ and engagement.",
            32: "Research shows that excessive social media use is linked to increased _____ among teenagers.",
            33: "The constant comparison with others can lead to feelings of _____ and low self-esteem.",
            34: "However, social media can provide valuable _____ for people feeling isolated."
        }
        return sentences.get(num, "")
    
    def get_section4_note(self, num: int) -> str:
        """Get note completion for Section 4"""
        notes = {
            35: "Participants who used social media for more than _____ hours per day showed higher anxiety levels",
            36: "The effect was strongest among _____ users",
            37: "Found that taking a _____ from social media improved wellbeing",
            38: "Participants reported better _____ after the break",
            39: "Set daily _____ for social media use",
            40: "Engage in more _____ interactions"
        }
        return notes.get(num, "")