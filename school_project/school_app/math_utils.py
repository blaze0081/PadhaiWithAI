# school_app/math_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def init_openai():
    return OpenAI(api_key=api_key)

def solve_math_problem(question, language="English"):
    client = init_openai()
    
    system_message = """You are an experienced mathematics teacher. Solve the questions given, following these guidelines:
    1. Include step-by-step solutions
    2. Use LaTeX formatting for mathematical expressions (use $ for inline math and $$ for display math)
    3. Show complete solution with final answers
    4. Explain concepts in simple terms
    5. Use examples and counter-examples
    6. Make solutions easy to understand"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Please solve this mathematics question step by step: {question}"}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def generate_similar_questions(question, difficulty, num_questions, language="English"):
    client = init_openai()
    
    system_message = f"""You are an experienced mathematics teacher. Generate {num_questions} new {difficulty} level variations of the given question.
    1. Use LaTeX formatting for mathematical expressions
    2. Maintain the same mathematical concept but vary complexity
    3. Include step-by-step solutions
    4. Explain in simple terms"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Generate variations of this question: {question}"}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content