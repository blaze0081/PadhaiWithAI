import os
from dotenv import load_dotenv
import google.generativeai as genai
from .solution_formatter import format_solution  

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def init_gemini():
    """Initialize the Gemini API client"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

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
    Generate similar mathematics questions with specified parameters using Gemini API.
    
    Args:
        question: Original question to base variations on
        difficulty: Desired difficulty level
        num_questions: Number of questions to generate
        language: Language for questions and solutions
        question_type: Type of questions to generate
    
    Returns:
        Formatted string containing generated questions and solutions
    """
    model = init_gemini()
    
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
    
    # Combine system message and prompt for Gemini
    full_prompt = f"{system_message}\n\n{prompt}"
    
    response = model.generate_content(full_prompt)
    
    # generated_content = response.text
    raw_solution = response.candidates[0].content.parts[0].text
    return format_solution(raw_solution)

def solve_math_problem(question: str, language: str = "English") -> str:
    """Solve a given mathematics problem with detailed explanation using Gemini API."""
    model = init_gemini()
    
    system_messages = {
        "Hindi": """आप एक अनुभवी गणित शिक्षक हैं। प्रश्न का हल इन नियमों का पालन करते हुए करें:
            1. गणितीय अभिव्यक्तियों के लिए LaTeX का उपयोग करें
            2. चरण-दर-चरण समाधान दें
            3. अवधारणाओं को सरल शब्दों में समझाएं
            4. उदाहरण और प्रति-उदाहरण दें
            5. तकनीकी शब्दों को सरल भाषा में समझाएं""",
            
        "English": """You are an experienced mathematics teacher. Solve the question following these guidelines:
        1. Use ^^ for inline LaTeX expressions (e.g., ^^x^2^^)
        2. Use '' for display LaTeX expressions (e.g., ''\\frac{1}{2}'')
        3. Mark each step clearly with **Step 1:**, **Step 2:**, etc.
        4. Explain concepts in simple terms
        5. Use proper formatting for mathematical expressions
        """
    }
    
    full_prompt = f"{system_messages[language]}\n\nPlease solve this mathematics question step by step: {question}"
    
    response = model.generate_content(full_prompt)
    # print(response.candidates[0].content.parts[0].text)
    raw_solution = response.candidates[0].content.parts[0].text
    return format_solution(raw_solution)