"""
Parser for IELTS Academic Reading Test Data
Extracts passages, questions, and answers from test documents
"""
from typing import Dict, List, Any

class ReadingTestParser:
    """Parse reading test questions and answers from document"""
    
    def parse_academic_test_1(self) -> Dict[str, Any]:
        """
        Parse Academic Reading Test 1 specifically
        Based on the provided document structure
        """
        
        # Test metadata
        test_data = {
            'test_id': 'academic-reading-test-1',
            'test_type': 'academic',
            'test_number': 1,
            'title': 'IELTS Academic Reading Test 1',
            'total_questions': 40,
            'duration_minutes': 60,
            'passages': [
                {
                    'number': 1,
                    'title': 'The History of Urban Vertical Farming',
                    'word_count': 850,
                    'question_range': '1-13',
                    'question_count': 13,
                    'time_recommended': 20
                },
                {
                    'number': 2,
                    'title': 'The Cognitive Benefits of Bilingualism',
                    'word_count': 900,
                    'question_range': '14-26',
                    'question_count': 13,
                    'time_recommended': 20
                },
                {
                    'number': 3,
                    'title': 'The Economics of Happiness',
                    'word_count': 950,
                    'question_range': '27-40',
                    'question_count': 14,
                    'time_recommended': 20
                }
            ]
        }
        
        # Parse questions
        questions = []
        
        # Passage 1: Questions 1-13
        # Questions 1-6: Paragraph matching
        for i in range(1, 7):
            questions.append({
                'number': i,
                'passage': 1,
                'type': 'paragraph_matching',
                'instructions': 'Which paragraph contains the following information? Write the correct letter, A-H',
                'text': self.get_passage1_paragraph_matching(i),
                'options': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            })
        
        # Questions 7-10: Multiple choice
        for i in range(7, 11):
            questions.append({
                'number': i,
                'passage': 1,
                'type': 'multiple_choice',
                'text': self.get_passage1_multiple_choice(i),
                'options': ['A', 'B', 'C', 'D']
            })
        
        # Questions 11-13: Sentence completion
        for i in range(11, 14):
            questions.append({
                'number': i,
                'passage': 1,
                'type': 'sentence_completion',
                'instructions': 'Choose NO MORE THAN THREE WORDS from the passage',
                'max_words': 3,
                'text': self.get_passage1_sentence_completion(i)
            })
        
        # Passage 2: Questions 14-26
        # Questions 14-18: True/False/Not Given
        for i in range(14, 19):
            questions.append({
                'number': i,
                'passage': 2,
                'type': 'true_false_not_given',
                'text': self.get_passage2_tfng(i),
                'options': ['TRUE', 'FALSE', 'NOT GIVEN']
            })
        
        # Questions 19-22: Matching groups
        for i in range(19, 23):
            questions.append({
                'number': i,
                'passage': 2,
                'type': 'matching',
                'text': self.get_passage2_matching(i),
                'options': ['A', 'B', 'C'],
                'option_descriptions': {
                    'A': 'Bilingual children',
                    'B': 'Bilingual adults',
                    'C': 'Both bilingual children and adults'
                }
            })
        
        # Questions 23-26: Summary completion
        for i in range(23, 27):
            questions.append({
                'number': i,
                'passage': 2,
                'type': 'summary_completion',
                'instructions': 'Choose NO MORE THAN TWO WORDS from the passage',
                'max_words': 2,
                'text': self.get_passage2_summary(i)
            })
        
        # Passage 3: Questions 27-40
        # Questions 27-30: Heading matching
        for i in range(27, 31):
            questions.append({
                'number': i,
                'passage': 3,
                'type': 'heading_matching',
                'text': self.get_passage3_heading(i),
                'options': ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
            })
        
        # Questions 31-35: Yes/No/Not Given
        for i in range(31, 36):
            questions.append({
                'number': i,
                'passage': 3,
                'type': 'yes_no_not_given',
                'text': self.get_passage3_ynng(i),
                'options': ['YES', 'NO', 'NOT GIVEN']
            })
        
        # Questions 36-40: Multiple choice
        for i in range(36, 41):
            questions.append({
                'number': i,
                'passage': 3,
                'type': 'multiple_choice',
                'text': self.get_passage3_multiple_choice(i),
                'options': ['A', 'B', 'C', 'D']
            })
        
        # Answer key with explanations
        answers = {
            '1': 'C',
            '2': 'F',
            '3': 'D',
            '4': 'G',
            '5': 'C',
            '6': 'H',
            '7': 'B',
            '8': 'B',
            '9': 'C',
            '10': 'D',
            '11': 'food miles',
            '12': 'extreme weather events',
            '13': 'city dwellers',
            '14': 'FALSE',
            '15': 'TRUE',
            '16': 'TRUE',
            '17': 'FALSE',
            '18': 'NOT GIVEN',
            '19': 'A',
            '20': 'B',
            '21': 'C',
            '22': 'A',
            '23': 'vocabularies',
            '24': 'tip-of-the-tongue',
            '25': 'mental lexicon',
            '26': 'vocabulary development',
            '27': 'i',
            '28': 'v',
            '29': 'iii',
            '30': 'ii',
            '31': 'NO',
            '32': 'YES',
            '33': 'NO',
            '34': 'NOT GIVEN',
            '35': 'NO',
            '36': 'B',
            '37': 'C',
            '38': 'B',
            '39': 'C',
            '40': 'B'
        }
        
        return {
            'test_data': test_data,
            'questions': questions,
            'answers': answers
        }
    
    # Passage 1 question getters
    def get_passage1_paragraph_matching(self, num: int) -> str:
        questions = {
            1: "a reference to the earliest published use of the term 'vertical farming'",
            2: "mention of the types of crops currently unsuitable for vertical farming",
            3: "a description of how LED technology benefits plant cultivation",
            4: "concerns about inequality in access to vertical farming produce",
            5: "the origins of hydroponic farming research in Asia",
            6: "potential future uses of renewable energy in vertical farming"
        }
        return questions.get(num, "")
    
    def get_passage1_multiple_choice(self, num: int) -> str:
        questions = {
            7: "According to the passage, Dickson Despommier's contribution to vertical farming was",
            8: "What does the writer suggest about vertical farming in the 1970s and 1980s?",
            9: "The main advantage of vertical farming in terms of water usage is that it",
            10: "According to the passage, which factor has prevented vertical farming from becoming widespread?"
        }
        return questions.get(num, "")
    
    def get_passage1_sentence_completion(self, num: int) -> str:
        sentences = {
            11: "Growing food locally through vertical farming reduces __________________, which lowers carbon emissions.",
            12: "Vertical farms protect crops from __________________, which are increasing due to climate change.",
            13: "Some urban planners believe vertical farms could help __________________ reconnect with food production."
        }
        return sentences.get(num, "")
    
    # Passage 2 question getters
    def get_passage2_tfng(self, num: int) -> str:
        statements = {
            14: "Bilingual people must use both languages simultaneously when speaking.",
            15: "Brain imaging studies show that managing two languages strengthens the prefrontal cortex.",
            16: "Bilingual individuals develop dementia symptoms later than monolinguals with similar backgrounds.",
            17: "Bilingualism completely prevents the development of Alzheimer's disease.",
            18: "Research shows that bilingual education always produces better academic results than monolingual education."
        }
        return statements.get(num, "")
    
    def get_passage2_matching(self, num: int) -> str:
        abilities = {
            19: "Better performance on attention control tasks",
            20: "Delayed onset of dementia symptoms",
            21: "Enhanced metalinguistic awareness",
            22: "Earlier development of theory of mind"
        }
        return abilities.get(num, "")
    
    def get_passage2_summary(self, num: int) -> str:
        gaps = {
            23: "Bilinguals may have slightly smaller __________________ in each language compared to monolinguals.",
            24: "They may also experience __________________ moments when they cannot retrieve a specific word.",
            25: "This happens because their __________________ must accommodate two languages.",
            26: "Additionally, bilingual children might show slower __________________ initial development."
        }
        return gaps.get(num, "")
    
    # Passage 3 question getters
    def get_passage3_heading(self, num: int) -> str:
        paragraphs = {
            27: "Paragraph B",
            28: "Paragraph D",
            29: "Paragraph F",
            30: "Paragraph H"
        }
        return paragraphs.get(num, "")
    
    def get_passage3_ynng(self, num: int) -> str:
        statements = {
            31: "Economic growth is the most important goal for any society to pursue.",
            32: "People living in poverty experience significant improvements in happiness when their income increases.",
            33: "All cultures define and value happiness in exactly the same way.",
            34: "Scandinavian countries are happy primarily because of their high income levels.",
            35: "Governments should focus exclusively on economic metrics rather than happiness."
        }
        return statements.get(num, "")
    
    def get_passage3_multiple_choice(self, num: int) -> str:
        questions = {
            36: "The Easterlin Paradox suggests that",
            37: "According to the passage, hedonic adaptation means that",
            38: "Research on lottery winners indicates that",
            39: "The research by Kahneman and Deaton found that",
            40: "What is the writer's main point about happiness economics?"
        }
        return questions.get(num, "")