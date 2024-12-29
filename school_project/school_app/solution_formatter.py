import re

def format_solution(raw_solution: str) -> str:
    """
    Format the raw solution text from Gemini API into structured HTML with proper LaTeX.
    
    Args:
        raw_solution: The raw solution text from the API
        
    Returns:
        Formatted HTML string with proper structure and LaTeX
    """
    # Split into steps
    steps = re.split(r'\*\*Step \d+:', raw_solution)
    if len(steps) <= 1:  # If no step markers found, split by newlines
        steps = raw_solution.split('\n')
    
    # Format each step
    formatted_steps = []
    for step in steps:
        if not step.strip():
            continue
            
        # Format LaTeX expressions
        step = re.sub(r'\^\^(.*?)\^\^', r'$\1$', step)  # Convert ^^ to $ for inline math
        step = re.sub(r"''(.*?)''", r'$$\1$$', step)    # Convert '' to $$ for display math
        
        # Wrap step in formatted div
        formatted_step = f'''
        <div class="solution-step">
            <div class="step-content">
                {step.strip()}
            </div>
        </div>
        '''
        formatted_steps.append(formatted_step)
    
    # Combine all steps into final HTML
    formatted_solution = f'''
    <div class="structured-solution">
        {''.join(formatted_steps)}
    </div>
    '''
    
    return formatted_solution