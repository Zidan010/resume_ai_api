import os
import re
import json
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from groq import Groq
import time
import random
import pdfplumber
from typing import Dict, Any, Optional
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
app = FastAPI()

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # Ensure GROQ_API_KEY is set in your environment

CV_STRUCTURE_SCHEMA = {
    "title": "CVStructure",
    "description": "Structured representation of a curriculum vitae (CV) extracted from text.",
    "type": "object",
    "properties": {
        "personal_info": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "email": {"type": "array", "items": {"type": "string"}},
                "phone": {"type": "array", "items": {"type": "string"}},
                "linkedin": {"type": ["string", "null"]},
                "address": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["full_name", "email", "phone", "linkedin", "address", "city", "country"]
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "result": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["degree", "institution", "start_date", "end_date", "result"]
            }
        },
        "work_experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "dates": {"type": "string"},
                    "responsibilities": {"type": "array", "items": {"type": "string"}},
                    "achievements": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["job_title", "company", "dates", "responsibilities", "achievements"]
            }
        },
        "skills": {
            "type": "object",
            "properties": {
                "technical": {"type": "array", "items": {"type": "string"}},
                "professional": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["technical", "professional"]
        },
        "projects": {
            "type": "array",
            "items": {"type": "object"}
        },
        "publications": {
            "type": "array",
            "items": {"type": "object"}
        },
        "certifications": {
            "type": "array",
            "items": {"type": "object"}
        },
        "awards": {
            "type": "array",
            "items": {"type": "object"}
        },
        "references": {
            "type": "array",
            "items": {"type": "object"}
        },
        "hobbies": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["personal_info", "education", "work_experience", "skills", "projects", "publications", "certifications", "awards", "references", "hobbies"]
}

# Pydantic model for CV structure response
class CVStructureResponse(BaseModel):
    parsed_cv: Dict[str, Any]
    execution_time: float

# Pydantic model for CV summary request
class CVSummaryRequest(BaseModel):
    professional_background: str
    quantifiable_achievements: str
    skills_and_certifications: str
    education: str
    target_role_company: str
    career_goals: Optional[str]
    word_length: Optional[int] = 75

# Pydantic model for responsibility request
class ResponsibilityRequest(BaseModel):
    job_title: str
    company_industry: str

# Pydantic model for skills request
class SkillsRequest(BaseModel):
    job_title: str

# Pydantic model for response
class APIResponse(BaseModel):
    generated_summary: str
    word_count: int
    execution_time: float
    temperature: float

def clean_output(text: str, output_type: str) -> str:
    """
    Clean the generated output based on the output type (summary, responsibilities, skills).
    Removes harmful special characters, normalizes whitespace, and formats appropriately.
    
    Args:
        text: Raw output from the Groq API
        output_type: One of 'summary', 'responsibilities', or 'skills'
    
    Returns:
        Cleaned and formatted text
    # """
    # # Define harmful special characters to remove (allow %, ,, ' for valid use)
    # harmful_chars = r'[\*\\/#<>]'
    
    # # Remove harmful characters and normalize whitespace
    # cleaned_text = re.sub(harmful_chars, '', text)
    # cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    if output_type == 'summary':
        # Define harmful special characters to remove (allow %, ,, ' for valid use)
        harmful_chars = r'[\*\\/#<>]'
        
        # Remove harmful characters and normalize whitespace
        cleaned_text = re.sub(harmful_chars, '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        # For summary: Ensure proper sentence structure, handle single or multiple sentences
        sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
        if not sentences:  # Handle empty or malformed input
            return ""
        cleaned_sentences = [s + '.' for s in sentences if not s.endswith('.')]
        cleaned_sentences = [s[:-1] if s.endswith('..') else s for s in cleaned_sentences]
        return ' '.join(cleaned_sentences) if cleaned_sentences else cleaned_text + '.'
    
    elif output_type == 'responsibilities':
        # Define harmful special characters to remove (allow %, ,, ' for valid use)
        harmful_chars = r'[\*\\/#<>]'
        
        # Remove harmful characters and normalize whitespace
        cleaned_text = re.sub(harmful_chars, '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        # For responsibilities: Separate sentences with \n, ensure proper formatting
        sentences = [s.strip() for s in cleaned_text.split('.') if s.strip()]
        if not sentences:
            return ""
        cleaned_sentences = [s + '.' for s in sentences if not s.endswith('.')]
        cleaned_sentences = [s[:-1] if s.endswith('..') else s for s in cleaned_sentences]
        return '\n'.join(cleaned_sentences)
    
    elif output_type == 'skills':
        # Define harmful special characters to remove (allow %, ,, ' for valid use)
        harmful_chars = r'[\*\\/#<>]'
        
        # Remove harmful characters and normalize whitespace
        cleaned_text = re.sub(harmful_chars, '', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        skills = []
        for s in re.split(r'[,\.\n]\s*', cleaned_text):
            # Clean each potential skill
            skill = re.sub(r'[^\w\s-]', '', s).strip()
            if skill:
                skills.append(skill)
        if not skills:
            print(f"Debug: No valid skills found. Raw: {cleaned_text}")
            return ""
        # Format as 'skill1', 'skill2', ...
        formatted_skills = [f"'{s}'" for s in skills]
        result = ', '.join(formatted_skills)
        print(f"Debug: Cleaned skills: {result}")
        return result
    
    elif output_type == 'cv_structure':
        try:
            json_data = json.loads(text) if isinstance(text, str) else text
            def clean_text_fields(data):
                if isinstance(data, str):
                    # Preserve / in GPA formats, remove other harmful characters
                    cleaned = re.sub(r'[\*\><]', '', data)
                    return re.sub(r'\s+', ' ', cleaned).strip()
                elif isinstance(data, list):
                    return [clean_text_fields(item) for item in data]
                elif isinstance(data, dict):
                    return {k: clean_text_fields(v) for k, v in data.items()}
                return data
            result = json.dumps(clean_text_fields(json_data))
            return result
        except json.JSONDecodeError:
            return text
        


    else:
        raise ValueError(f"Invalid output_type: {output_type}")


@app.post("/generate/cv_summary", response_model=APIResponse)
async def generate_cv_summary(request: CVSummaryRequest):
    try:
        # Extract request data
        word_length = request.word_length
        range_a = word_length - random.randint(5, 6)# max(50, word_length - random.randint(5, 10))
        range_b = word_length + random.randint(5, 6)#min(100, word_length + random.randint(5, 10))
        max_tokens = 1024
        temperature = round(random.uniform(0.2, 0.5), 2)

        # Create user prompt
        user_message = (
            f"Professional Background: '{request.professional_background}', "
            f"Quantifiable Achievements: '{request.quantifiable_achievements}', "
            f"Skills and Certifications: '{request.skills_and_certifications}', "
            f"Education: '{request.education}', "
            f"Target Role/Company: '{request.target_role_company}', "
            f"Career Goals: '{request.career_goals if request.career_goals else 'Not specified'}'. "
            f"Ensure the summary is persuasive, tailored to the target role, and suitable for a professional CV. "
            f"Provide only the summary using multiple sentences, without any additional text."
        )

        # Start timing
        start_time = time.time()

        # Generate summary using Groq API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional resume summary writer. Your task is to generate a detailed, engaging, and professional resume summary "
                        f"within {range_a} to {range_b} words based on provided details."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # End timing
        execution_time = time.time() - start_time

        # Extract generated summary
        generated_summary = response.choices[0].message.content
        print(generated_summary)
        generated_summary = clean_output(generated_summary, output_type="summary")
        word_count = len(generated_summary.split())


        return APIResponse(
            generated_summary=generated_summary,
            word_count=word_count,
            execution_time=execution_time,
            temperature=temperature
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.post("/generate/job-responsibilities", response_model=APIResponse)
async def generate_responsibilities(request: ResponsibilityRequest):
    try:
        # Model generation parameters
        max_tokens = 1024
        temperature = round(random.uniform(0.2, 0.5), 2)

        # Create user prompt
        user_message = (
            f"You are a professional job responsibility writer. Generate concise and professional job responsibilities based on: "
            f"Job Title: '{request.job_title}', "
            f"Company Industry: '{request.company_industry}'. "
            f"Ensure the Job Responsibilities are persuasive, tailored to the target Job Title and Company and suitable for a professional CV. "
            f"Provide 3-5 sentences of Job Responsibilities only, without any additional text."
        )

        # Start timing
        start_time = time.time()

        # Generate responsibilities using Groq API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional job responsibilities writer. Your task is to generate detailed, engaging, and professional job responsibilities "
                        f"based on provided details."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # End timing
        execution_time = time.time() - start_time

        # Extract generated responsibilities
        generated_summary = response.choices[0].message.content
        print(generated_summary)
        generated_summary = clean_output(generated_summary, output_type="responsibilities")
        word_count = len(generated_summary.split())

        # Post-process to format as list
        sentences = generated_summary.split('. ')
        formatted_summary = '\n'.join(sentence.strip() + ('.' if not sentence.endswith('.') else '') for sentence in sentences if sentence.strip())

        return APIResponse(
            generated_summary=formatted_summary,
            word_count=word_count,
            execution_time=execution_time,
            temperature=temperature
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating responsibilities: {str(e)}")

@app.post("/generate/skills", response_model=APIResponse)
async def suggest_skills(request: SkillsRequest):
    try:
        # Model generation parameters
        max_tokens = 1024
        temperature = round(random.uniform(0.2, 0.5), 2)

        # Create user prompt
        user_message = (
            f"You are a professional job skills writer. Generate concise and professional job skills for the job title '{request.job_title}'. "
            f"Provide maximum 6-8 skills as a comma-separated list of single words or short phrases (e.g., 'html, css, scrum master, critical thinking'). "
            f"Ensure the skills are persuasive, tailored to the job title, and suitable for a professional CV. "
            f"Provide only the skills list, without any additional text or formatting."
        )

        # Start timing
        start_time = time.time()

        # Generate skills using Groq API
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional job skills writer. Generate 5-10 concise, professional skills as a comma-separated list of single words or short phrases "
                        f"(e.g., 'html, css, scrum master, critical thinking') based on the provided job title."
                    )
                },
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # End timing
        execution_time = time.time() - start_time

        # Extract and clean generated skills
        generated_summary = response.choices[0].message.content
        print(f"Debug: Raw skills output: {generated_summary}")
        cleaned_summary = clean_output(generated_summary, output_type="skills")
        word_count = len(cleaned_summary.split())

        # Debug if output is commas or empty
        if generated_summary.strip() in [",", ",,,", ",,,..."]:
            print(f"Debug: Comma-heavy output detected in skills: {generated_summary}")
            print("Debug: Check model response for unexpected behavior.")
        if not cleaned_summary:
            print(f"Debug: Empty cleaned summary for skills. Raw output: {generated_summary}")

        return APIResponse(
            generated_summary=cleaned_summary,
            word_count=word_count,
            execution_time=execution_time,
            temperature=temperature
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating skills: {str(e)}")

@app.post("/generate/cv_structure", response_model=CVStructureResponse)
async def generate_cv_structure(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save uploaded PDF to temporary file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        try:
            # Extract text from PDF
            with pdfplumber.open(temp_file_path) as pdf:
                input_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if not input_text.strip():
                raise ValueError("No text extracted from PDF")

            # System prompt for CV parsing
            system_prompt = (
                "You are a professional CV parsing assistant. Extract key information from the provided CV text and structure it according to the provided JSON schema. "
                "Ensure all required fields are populated, inferring reasonable defaults for missing data where possible (e.g., empty arrays for optional fields like projects, publications)."
            )

            # User prompt
            user_message = (
                f"CV Text:\n{input_text}\n\n"
                f"Extract and structure the CV data into the following JSON schema:\n{json.dumps(CV_STRUCTURE_SCHEMA, indent=2)}\n\n"
                f"Return the parsed CV data as a JSON object."
            )

            # Start timing
            start_time = time.time()

            # Generate structured CV using Groq API
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=4096,  # Increased to handle complex CVs
                temperature=0.5,
                response_format={"type": "json_object"}  # Enforce JSON output
            )

            # End timing
            execution_time = time.time() - start_time

            # Extract and clean generated JSON
            generated_json = response.choices[0].message.content
            cleaned_json = clean_output(generated_json, output_type="cv_structure")
            parsed_cv = json.loads(cleaned_json)

            # Clean up temporary file
            os.unlink(temp_file_path)

            return CVStructureResponse(
                parsed_cv=parsed_cv,
                execution_time=execution_time
            )

        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise ValueError(f"Failed to process PDF: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CV structure: {str(e)}")


import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)






# {
# "professional_background" : "10 years of experience as a software engineer at TechCorp, specializing in full-stack development and leading agile teams.",
# "quantifiable_achievements" : "Developed 5 high-traffic web applications, increasing user engagement by 30%; reduced deployment time by 40% through CI/CD pipeline optimization.",
# "skills_and_certifications" : "Python, JavaScript, AWS, Docker; AWS Certified Solutions Architect, Scrum Master.",
# "education" : "B.S. in Computer Science, Stanford University, 2012.",
# "target_role_company" : "Senior Software Engineer at InnovateTech.",
# "career_goals" : "To lead innovative software projects that leverage cloud technologies and drive business growth.",
#   "word_length": 75
# }


