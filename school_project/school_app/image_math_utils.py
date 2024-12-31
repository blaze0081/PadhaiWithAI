import os
import base64
from typing import Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from .solution_formatter import format_solution

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'school_app', 'images', 'geometry')

def init_vision_model():
    """Initialize the Gemini Vision API client"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro-vision')

def get_image_path(image_reference: str) -> Optional[str]:
    """Get the full path for an image based on its reference."""
    filename = f"{image_reference.lower().replace(' ', '_')}.png"
    image_path = os.path.join(IMAGES_DIR, filename)
    return image_path if os.path.exists(image_path) else None

def encode_image(image_path: str) -> str:
    """Encode image to base64 for Gemini API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_vision_system_message(language: str) -> str:
    """Returns the appropriate system message for image-based questions."""
    system_messages = {
        "Hindi": """आप एक अनुभवी गणित शिक्षक हैं। दिए गए चित्र और प्रश्न का विश्लेषण करें और इन नियमों का पालन करें:
            1. गणितीय अभिव्यक्तियों को लिखने के लिए LaTeX फॉर्मेटिंग का उपयोग करें
            2. चरण-दर-चरण समाधान प्रदान करें
            3. आरेख में दिखाए गए महत्वपूर्ण बिंदुओं और रेखाओं का उल्लेख करें
            4. ज्यामितीय अवधारणाओं को सरल शब्दों में समझाएं""",
            
        "English": """You are an experienced mathematics teacher. Analyze the given figure and question following these guidelines:
            1. Use LaTeX formatting for mathematical expressions
            2. Provide step-by-step solutions
            3. Reference important points and lines shown in the diagram
            4. Explain geometric concepts in simple terms
            5. When analyzing figures, start by listing all given information
            6. Use proper geometric terminology while keeping explanations accessible"""
    }
    return system_messages.get(language, system_messages["English"])

def solve_visual_math_problem(question: str, image_reference: str, language: str = "English") -> str:
    """
    Solve a mathematics problem that requires visual context using Gemini Vision API.
    
    Args:
        question: The question text
        image_reference: Reference to the required image (e.g., "Figure 6.8")
        language: Language for the response
        
    Returns:
        Formatted solution with step-by-step explanation
    """
    try:
        model = init_vision_model()
        image_path = get_image_path(image_reference)
        
        if not image_path:
            return f"Error: Image {image_reference} not found"
            
        image_data = {
            "mime_type": "image/png",
            "data": encode_image(image_path)
        }
        
        system_message = get_vision_system_message(language)
        question_with_context = f"For the geometric figure {image_reference}:\n{question}"
        full_prompt = f"{system_message}\n\nPlease solve this mathematics question step by step: {question_with_context}"
        
        response = model.generate_content([full_prompt, image_data])
        raw_solution = response.text
        return format_solution(raw_solution)
        
    except Exception as e:
        return f"Error processing image-based question: {str(e)}"

def generate_similar_visual_questions(
    question: str, 
    image_reference: str,
    difficulty: str,
    num_questions: int,
    language: str = "English"
) -> str:
    """
    Generate similar mathematics questions based on a visual example.
    
    Args:
        question: Original question to base variations on
        image_reference: Reference to the required image
        difficulty: Desired difficulty level
        num_questions: Number of questions to generate
        language: Language for questions and solutions
        
    Returns:
        Formatted string containing generated questions and solutions
    """
    try:
        model = init_vision_model()
        image_path = get_image_path(image_reference)
        
        if not image_path:
            return f"Error: Image {image_reference} not found"
            
        image_data = {
            "mime_type": "image/png",
            "data": encode_image(image_path)
        }
        
        system_message = get_vision_system_message(language)
        prompt = f"""Based on this example question and figure, generate {num_questions} new questions 
        at {difficulty} difficulty level:
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
        
        full_prompt = f"{system_message}\n\n{prompt}"
        response = model.generate_content([full_prompt, image_data])
        raw_solution = response.text
        return format_solution(raw_solution)
        
    except Exception as e:
        return f"Error generating similar visual questions: {str(e)}"