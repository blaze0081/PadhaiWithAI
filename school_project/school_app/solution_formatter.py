import re
import markdown

class SolutionFormatter:
    """
    Handles the formatting of questions and solutions from raw text/markdown to HTML.
    This version isolates all standard LaTeX math delimiters before markdown processing
    to prevent syntax conflicts and ensure correct rendering by MathJax.
    """

    @staticmethod
    def _format_content(text: str) -> str:

        """
        A robust method to convert mixed Markdown and LaTeX text to HTML.
        It isolates math expressions, processes the Markdown, and then restores the math.
        """
        math_expressions = []

        def store_math(match):
            """Stores the math expression and returns an HTML comment placeholder."""
            index = len(math_expressions)
            math_expressions.append(match.group(0))
            return f'<!--MATH_PLACEHOLDER_{index}-->'

        # This robust pattern finds all standard LaTeX delimiters.
        pattern = re.compile(
            r'('            # Start capturing group for all math patterns
            r'(?:\$\$.*?\$\$)|'  # Match $$...$$
            r'(?:\\\[.*?\\\])|'  # Match \[...\]
            r'(?:\$[^\$\n]+\$)|'  # Match $...$ (safer, non-greedy version)
            r'(?:\\\(.*?\\\))'   # Match \(...\)
            r')',             # End capturing group
            re.DOTALL
        )

        # Replace math expressions with HTML comment placeholders
        text_with_placeholders = pattern.sub(store_math, text)

        # Convert the full text to HTML. Markdown processor ignores comments.
        html_content = markdown.markdown(text_with_placeholders, extensions=['extra', 'sane_lists'])

        # Restore the original math expressions
        for i, math_expr in enumerate(math_expressions):
            placeholder = f'<!--MATH_PLACEHOLDER_{i}-->'
            html_content = html_content.replace(placeholder, math_expr)

        return html_content

    @staticmethod
    def format_solution(solution_text: str) -> str:
        """
        Formats the raw solution text into clean HTML for rendering.
        """
        return SolutionFormatter._format_content(solution_text)

    @staticmethod
    def format_question(question_text: str) -> str:
        """
        Formats the raw question text into clean HTML for rendering.
        """
        return SolutionFormatter._format_content(question_text)
