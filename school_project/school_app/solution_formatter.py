import re
import markdown
from bs4 import BeautifulSoup

class SolutionFormatter:
    @staticmethod
    def format_solution(solution_text):
        """Format the solution text with proper markdown and LaTeX formatting."""
        # Split into steps based on double asterisks
        steps = re.split(r'\*\*(.*?)\*\*', solution_text)
        
        formatted_steps = []
        for i, step in enumerate(steps):
            if i % 2 == 0:  # Content between headers
                if step.strip():
                    # Process mathematical expressions
                    step = SolutionFormatter._format_math(step)
                    formatted_steps.append(f'<div class="step-content">{step}</div>')
            else:  # Headers
                formatted_steps.append(f'<h4 class="step-title">{step}</h4>')
        
        # Join all steps and convert markdown to HTML
        formatted_solution = '\n'.join(formatted_steps)
        html_content = markdown.markdown(formatted_solution)
        
        # Wrap in a structured solution div
        return f'<div class="structured-solution">{html_content}</div>'
    
    @staticmethod
    def _format_math(text):
        """Format mathematical expressions."""
        # Replace inline math delimiters
        text = re.sub(r'(?<!\\)\$(.+?)(?<!\\)\$', r'\\(\1\\)', text)
        
        # Format fractions
        text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
        
        # Format subscripts (e.g., a1 -> a_1)
        text = re.sub(r'([a-zA-Z])(\d+)', r'\1_\2', text)
        
        return text
    
    @staticmethod
    def format_question(question_text):
        """Format the question text."""
        # Process mathematical expressions
        question = SolutionFormatter._format_math(question_text)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(question)
        
        return html_content
