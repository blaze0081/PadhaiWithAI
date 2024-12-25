import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def init_openai():
    return OpenAI(api_key=api_key)

def format_math_content(content: str) -> str:
    """Formats mathematical content consistently for both display and download."""
    sections = content.split('\n\n')
    formatted_sections = []
    
    current_section = None
    current_items = []
    
    for section in sections:
        if section.strip().startswith('Questions:') or section.strip().startswith('प्रश्न:'):
            if current_section and current_items:
                formatted_sections.append(f"{current_section}\n" + "\n\n".join(current_items))
            current_section = "Questions:" if "Questions:" in section else "प्रश्न:"
            current_items = []
        elif section.strip().startswith('Answers:') or section.strip().startswith('उत्तर:'):
            if current_section and current_items:
                formatted_sections.append(f"{current_section}\n" + "\n\n".join(current_items))
            current_section = "Answers:" if "Answers:" in section else "उत्तर:"
            current_items = []
        else:
            lines = section.strip().split('\n')
            formatted_item = []
            
            for line in lines:
                if re.match(r'^\d+\.', line):
                    if formatted_item:
                        current_items.append('\n'.join(formatted_item))
                        formatted_item = []
                    formatted_item.append(line)
                elif re.match(r'^[a-d]\)', line):
                    formatted_item.append(line)
                elif line.strip().startswith('Steps:') or line.strip().startswith('चरण:'):
                    formatted_item.append('\n' + line)
                else:
                    formatted_item.append(line)
            
            if formatted_item:
                current_items.append('\n'.join(formatted_item))
    
    if current_section and current_items:
        formatted_sections.append(f"{current_section}\n" + "\n\n".join(current_items))
    
    return '\n\n'.join(formatted_sections)

def get_system_message(language: str, difficulty: str, question_type: str) -> str:
    """Returns the appropriate system message based on language and question type."""
    
    system_messages = {
        "Hindi": f"""आप एक अनुभवी गणित शिक्षक हैं। दिए गए उदाहरणों की तरह प्रश्न बनाएं और इन नियमों का पालन करें:
            1. गणितीय अभिव्यक्तियों को लिखने के लिए LaTeX फॉर्मेटिंग का उपयोग करें (इनलाइन गणित के लिए $ और बड़े गणित के लिए $$ का उपयोग करें)।
            2. कठिनाई स्तर '{difficulty}' पर सेट करें।
            3. प्रश्न प्रारूप '{question_type}' में होना चाहिए।
            4. प्रत्येक प्रश्न के लिए विस्तृत चरण-दर-चरण समाधान प्रदान करें।
            5. समाधान में अवधारणाओं को सरल शब्दों में समझाएं।
            6. उदाहरण और प्रति-उदाहरण दें।
            7. तकनीकी शब्दों को सरल भाषा में समझाएं।""",
            
        "English": f"""You are an experienced mathematics teacher. Generate questions similar to the given examples, following these guidelines:
            1. Use LaTeX formatting for mathematical expressions (use $ for inline math and $$ for display math)
            2. Set difficulty level to '{difficulty}'
            3. Create questions in '{question_type}' format
            4. Provide detailed step-by-step solutions for each question
            5. Explain concepts in simple terms
            6. Include examples and counter-examples
            7. Explain technical terms in simple language"""
    }
    
    return system_messages.get(language, system_messages["English"])

def generate_similar_questions(question: str, difficulty: str, num_questions: int, 
                            language: str, question_type: str) -> str:
    """
    Generate similar mathematics questions with specified parameters.
    
    Args:
        question: Original question to base variations on
        difficulty: Desired difficulty level
        num_questions: Number of questions to generate
        language: Language for questions and solutions
        question_type: Type of questions to generate
    
    Returns:
        Formatted string containing generated questions and solutions
    """
    client = init_openai()
    
    system_message = get_system_message(language, difficulty, question_type)
    
    # Create language-specific prompts
    prompts = {
        "Hindi": f"""इस उदाहरण प्रश्न के आधार पर {num_questions} नए प्रश्न बनाएं:
            उदाहरण: {question}
            
            प्रश्नों को इस प्रकार संरचित करें:
            प्रश्न:
            1. [पहला प्रश्न]
            2. [दूसरा प्रश्न]
            ...
            
            उत्तर:
            1. [पहले प्रश्न का विस्तृत समाधान]
            2. [दूसरे प्रश्न का विस्तृत समाधान]
            ...""",
        
        "English": f"""Based on this example question, generate {num_questions} new questions:
            Example: {question}
            
            Structure the response as:
            Questions:
            1. [First question]
            2. [Second question]
            ...
            
            Answers:
            1. [Detailed solution for first question]
            2. [Detailed solution for second question]
            ..."""
    }
    
    prompt = prompts.get(language, prompts["English"])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    generated_content = response.choices[0].message.content
    return format_math_content(generated_content)

def solve_math_problem(question: str, language: str = "English") -> str:
    """Solve a given mathematics problem with detailed explanation."""
    client = init_openai()
    
    system_messages = {
        "Hindi": """आप एक अनुभवी गणित शिक्षक हैं। प्रश्न का हल इन नियमों का पालन करते हुए करें:
            1. गणितीय अभिव्यक्तियों के लिए LaTeX का उपयोग करें
            2. चरण-दर-चरण समाधान दें
            3. अवधारणाओं को सरल शब्दों में समझाएं
            4. उदाहरण और प्रति-उदाहरण दें
            5. तकनीकी शब्दों को सरल भाषा में समझाएं""",
            
        "English": """You are an experienced mathematics teacher. Solve the question following these guidelines:
            1. Use LaTeX for mathematical expressions
            2. Provide step-by-step solutions
            3. Explain concepts in simple terms
            4. Include examples and counter-examples
            5. Explain technical terms in simple language"""
    }
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_messages[language]},
            {"role": "user", "content": f"Please solve this mathematics question step by step: {question}"}
        ],
        temperature=0.7
    )
    
    return format_math_content(response.choices[0].message.content)