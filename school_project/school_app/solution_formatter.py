import re
import markdown
from bs4 import BeautifulSoup

class SolutionFormatter:
    @staticmethod
    def format_solution(solution_text):
        """Format the solution text with clear sections and proper styling."""
        try:
            # Split into main sections
            sections = solution_text.split('#')
            formatted_sections = []
            
            for section in sections:
                if not section.strip():
                    continue
                    
                # Get section title and content
                parts = section.strip().split('\n', 1)
                if len(parts) < 2:
                    continue
                    
                title, content = parts
                
                # Format based on section type
                if "Original Questions" in title:
                    formatted_section = SolutionFormatter._format_original_questions(content)
                elif "Generated Questions" in title:
                    formatted_section = SolutionFormatter._format_generated_questions(content)
                elif "Solutions" in title:
                    formatted_section = SolutionFormatter._format_solutions(content)
                else:
                    continue
                
                formatted_sections.append(f'''
                <div class="section-container">
                    <h2 class="section-title">{title}</h2>
                    {formatted_section}
                </div>
                ''')
            
            return '\n'.join(formatted_sections)
            
        except Exception as e:
            print(f"Error formatting solution: {e}")
            return f'<div class="error">Error formatting content: {str(e)}</div>'

    @staticmethod
    def _format_original_questions(content):
        """Format original questions section."""
        questions = re.split(r'(\*\*Original Question \d+:\*\*)', content)
        formatted_questions = []
        
        for i in range(1, len(questions), 2):
            question_header = questions[i]
            question_content = questions[i + 1] if i + 1 < len(questions) else ""
            
            formatted_questions.append(f'''
            <div class="original-question">
                <h3 class="question-header">{question_header}</h3>
                <div class="question-content">{SolutionFormatter._format_math(question_content)}</div>
            </div>
            ''')
            
        return '\n'.join(formatted_questions)

    @staticmethod
    def _format_generated_questions(content):
        """Format generated questions section."""
        questions = re.split(r'(Question \d+\.\d+:)', content)
        formatted_questions = []
        
        for i in range(1, len(questions), 2):
            question_header = questions[i]
            question_content = questions[i + 1] if i + 1 < len(questions) else ""
            
            # Extract original question number for grouping
            orig_num = question_header.split('.')[0].split()[-1]
            
            formatted_questions.append(f'''
            <div class="generated-question" data-original-question="{orig_num}">
                <h4 class="question-header">{question_header}</h4>
                <div class="question-content">{SolutionFormatter._format_math(question_content)}</div>
            </div>
            ''')
            
        return '\n'.join(formatted_questions)

    @staticmethod
    def _format_solutions(content):
        """Format solutions section."""
        solutions = re.split(r'(Solution \d+\.\d+:)', content)
        formatted_solutions = []
        
        for i in range(1, len(solutions), 2):
            solution_header = solutions[i]
            solution_content = solutions[i + 1] if i + 1 < len(solutions) else ""
            
            # Extract original question number for grouping
            orig_num = solution_header.split('.')[0].split()[-1]
            
            formatted_solutions.append(f'''
            <div class="solution" data-original-question="{orig_num}">
                <h4 class="solution-header">{solution_header}</h4>
                <div class="solution-content">{SolutionFormatter._format_math(solution_content)}</div>
            </div>
            ''')
            
        return '\n'.join(formatted_solutions)
