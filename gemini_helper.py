import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Gemini API client if API key exists
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_resume_info(resume_text: str) -> dict:
    """
    Extracts structured information from resume text using Gemini.
    Returns a dictionary matching the specified schema.
    """
    load_dotenv(override=True)
    # Check key configuration again at call time in case .env was updated post-import
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
    
    genai.configure(api_key=current_key)
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
You are a resume parsing assistant. Analyze the resume text below and extract its structured content.
Return ONLY a valid JSON object with the keys specified in the schema. Do not wrap the response in markdown blocks (like ```json ... ```), return it as raw text.

Schema:
{{
  "skills": ["string", ...],
  "projects": [
    {{
      "name": "string",
      "description": "string"
    }},
    ...
  ],
  "experience": [
    {{
      "role": "string",
      "company": "string",
      "description": "string"
    }},
    ...
  ],
  "education": ["string", ...]
}}

Resume text:
{resume_text}
"""

    def call_and_parse():
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        content = response.text.strip()
        
        # Strip markdown json block wrappers if Gemini ignored the instruction
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)

    try:
        return call_and_parse()
    except Exception as e:
        # Retry once
        try:
            return call_and_parse()
        except Exception as retry_error:
            raise Exception(f"Failed to parse resume text after retrying: {retry_error}")

def generate_questions(resume_info: dict) -> list:
    """
    Generates 8 interview questions based on the structured resume profile.
    Returns a list of dictionaries with keys: question, topic, difficulty, model_answer.
    """
    load_dotenv(override=True)
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
    
    genai.configure(api_key=current_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
You are a technical interviewer. Analyze the following structured resume details:
{json.dumps(resume_info, indent=2)}

Generate exactly 8 interview questions based on this profile:
- 3 questions probing their "skills" (based on their skills list)
- 3 questions probing their "projects" (focusing on project details, design choices, or implementation details)
- 1 question probing their "experience" (focusing on their roles, companies, or responsibilities)
- 1 question probing their "education" (related to their academic background or coursework)

For each question, provide a suggested model answer. Return ONLY a valid JSON array of objects with the specified keys. Do not wrap the response in markdown blocks (like ```json ... ```), return it as raw text.

Required keys in each object:
- "question": "The interview question text"
- "topic": "The specific skill, project, experience, or education item this question is probing"
- "difficulty": "Easy" or "Medium" or "Hard"
- "model_answer": "A concise guidelines/answer indicating what a strong candidate response looks like"
"""

    def call_and_parse():
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        content = response.text.strip()
        
        # Strip markdown json block wrappers if Gemini ignored the instruction
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)

    try:
        return call_and_parse()
    except Exception as e:
        # Retry once
        try:
            return call_and_parse()
        except Exception as retry_error:
            raise Exception(f"Failed to generate interview questions after retrying: {retry_error}")

def get_feedback(question: str, model_answer: str, user_answer: str) -> dict:
    """
    Evaluates the user's answer against the model answer.
    Returns a dictionary with keys: score (int out of 10), feedback (2-3 sentences).
    """
    load_dotenv(override=True)
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
    
    genai.configure(api_key=current_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
You are a constructive interview coach. Compare the candidate's response to the expected model answer for the following question:

Question:
{question}

Expected Model Answer:
{model_answer}

Candidate's Answer:
{user_answer}

Provide feedback on the candidate's answer. Be constructive and encouraging, not harsh.
Return ONLY a valid JSON object with the following keys (do not wrap in markdown blocks like ```json ... ```):
{{
  "score": <int out of 10 reflecting the quality and completeness of the candidate's answer>,
  "feedback": "<a short 2-3 sentence critique highlighting what they did well and how they could improve>"
}}
"""

    def call_and_parse():
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        content = response.text.strip()
        
        # Strip markdown json block wrappers if Gemini ignored the instruction
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        return json.loads(content)

    try:
        return call_and_parse()
    except Exception as e:
        # Retry once
        try:
            return call_and_parse()
        except Exception as retry_error:
            raise Exception(f"Failed to generate feedback after retrying: {retry_error}")


