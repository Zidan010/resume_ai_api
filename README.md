# AI API Project for Resume

## Table of Contents
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [1. Generate CV Summary](#1-generate-cv-summary)
  - [2. Generate Job Responsibilities](#2-generate-job-responsibilities)
  - [3. Suggest Skills](#3-suggest-skills)
  - [4. Parse CV Structure from PDF](#4-parse-cv-structure-from-pdf)
  - [5. Generate ATS Score](#5-generate-ats-score)

---

## Setup

### Prerequisites
```bash
pip install fastapi uvicorn groq pdfplumber python-dotenv pydantic
```

### Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Running the Application
```bash
python main.py
```
The server will start at `http://localhost:9090`

---

## API Endpoints

### 1. Generate CV Summary

**Endpoint:** `POST /generate/cv_summary`

**Description:** Generates a professional CV summary tailored to a specific role based on provided candidate information.

**Request Body:**
```json
{
  "professional_background": "10 years of experience as a software engineer at TechCorp, specializing in full-stack development and leading agile teams.",
  "quantifiable_achievements": "Developed 5 high-traffic web applications, increasing user engagement by 30%; reduced deployment time by 40% through CI/CD pipeline optimization.",
  "skills_and_certifications": "Python, JavaScript, AWS, Docker; AWS Certified Solutions Architect, Scrum Master.",
  "education": "B.S. in Computer Science, Stanford University, 2012.",
  "target_role_company": "Senior Software Engineer at InnovateTech.",
  "career_goals": "To lead innovative software projects that leverage cloud technologies and drive business growth.",
  "word_length": 75
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| professional_background | string | Yes | Overview of professional experience |
| quantifiable_achievements | string | Yes | Measurable accomplishments |
| skills_and_certifications | string | Yes | Technical skills and certifications |
| education | string | Yes | Educational background |
| target_role_company | string | Yes | Target position and company |
| career_goals | string | No | Career objectives |
| word_length | integer | No | Desired word count (default: 75) |

**Response:**
```json
{
  "generated_summary": "Seasoned software engineer with 10 years of experience at TechCorp, specializing in full-stack development and agile team leadership. Proven track record of developing 5 high-traffic web applications that increased user engagement by 30% and optimized CI/CD pipelines to reduce deployment time by 40%. Proficient in Python, JavaScript, AWS, and Docker, with AWS Certified Solutions Architect and Scrum Master certifications. Holds a B.S. in Computer Science from Stanford University. Seeking Senior Software Engineer role at InnovateTech to lead innovative cloud-based projects driving business growth.",
  "word_count": 83,
  "execution_time": 2.45,
  "temperature": 0.35
}
```

---

### 2. Generate Job Responsibilities

**Endpoint:** `POST /generate/job-responsibilities`

**Description:** Generates professional job responsibilities for a specific role and industry.

**Request Body:**
```json
{
  "job_title": "Senior Software Engineer",
  "company_industry": "Cloud Computing & SaaS"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| job_title | string | Yes | Position title |
| company_industry | string | Yes | Company's industry sector |

**Response:**
```json
{
  "generated_summary": "Led cross-functional teams in designing and developing scalable cloud-based applications using microservices architecture.\nImplemented CI/CD pipelines and automated testing frameworks to ensure high-quality code delivery.\nCollaborated with product managers to translate business requirements into technical specifications.\nMentored junior developers and conducted code reviews to maintain coding standards.\nOptimized system performance and reduced infrastructure costs by 25% through efficient resource management.",
  "word_count": 68,
  "execution_time": 1.87,
  "temperature": 0.42
}
```

**Note:** Responsibilities are separated by newline characters (`\n`).

---

### 3. Suggest Skills

**Endpoint:** `POST /generate/skills`

**Description:** Suggests relevant professional skills for a given job title.

**Request Body:**
```json
{
  "job_title": "Data Scientist"
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| job_title | string | Yes | Position title for skill suggestions |

**Response:**
```json
{
  "generated_summary": "'Python', 'Machine Learning', 'Statistical Analysis', 'SQL', 'Data Visualization', 'TensorFlow', 'Deep Learning', 'Big Data'",
  "word_count": 8,
  "execution_time": 1.23,
  "temperature": 0.38
}
```

**Note:** Skills are returned as a formatted comma-separated list with single quotes.

---

### 4. Parse CV Structure from PDF

**Endpoint:** `POST /generate/cv_structure`

**Description:** Extracts structured information from a PDF resume and returns it in a standardized JSON format.

**Request:**
- Content-Type: `multipart/form-data`
- File parameter: `file` (PDF only)

**cURL Example:**
```bash
curl -X POST "http://localhost:9090/generate/cv_structure" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"
```

**Response:**
```json
{
  "parsed_cv": {
    "personal_info": {
      "full_name": "John Doe",
      "email": ["john.doe@email.com"],
      "phone": ["+1-234-567-8900"],
      "linkedin": "linkedin.com/in/johndoe",
      "address": "123 Main Street",
      "city": "San Francisco",
      "country": "USA"
    },
    "education": [
      {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "Stanford University",
        "start_date": "2008",
        "end_date": "2012",
        "result": ["GPA: 3.8/4.0"]
      }
    ],
    "work_experience": [
      {
        "job_title": "Senior Software Engineer",
        "company": "TechCorp Inc.",
        "dates": "2016 - Present",
        "responsibilities": [
          "Led development of cloud-based applications",
          "Managed team of 5 developers"
        ],
        "achievements": [
          "Reduced system latency by 40%",
          "Implemented microservices architecture"
        ]
      }
    ],
    "skills": {
      "technical": ["Python", "JavaScript", "AWS", "Docker", "Kubernetes"],
      "professional": ["Team Leadership", "Agile Methodologies", "Communication"]
    },
    "projects": [],
    "publications": [],
    "certifications": [
      {
        "name": "AWS Certified Solutions Architect",
        "issuer": "Amazon Web Services",
        "date": "2020"
      }
    ],
    "awards": [],
    "references": [],
    "hobbies": ["Photography", "Hiking"]
  },
  "execution_time": 3.67
}
```

**CV Structure Schema:**
The parsed CV follows a standardized schema with the following sections:
- **personal_info**: Name, contact details, location
- **education**: Degrees, institutions, dates, results
- **work_experience**: Job titles, companies, responsibilities, achievements
- **skills**: Technical and professional skills
- **projects**: Project details (optional)
- **publications**: Publications list (optional)
- **certifications**: Professional certifications (optional)
- **awards**: Awards and honors (optional)
- **references**: Professional references (optional)
- **hobbies**: Personal interests (optional)

---

### 5. Generate ATS Score

**Endpoint:** `POST /generate/ats_score`

**Description:** Analyzes a CV against a job description and provides an ATS (Applicant Tracking System) compatibility score with detailed feedback.

**Request Body:**
```json
{
  "cv_data": {
    "personal_info": {
      "full_name": "John Doe",
      "email": ["john.doe@email.com"],
      "phone": ["+1234567890"],
      "linkedin": "linkedin.com/in/johndoe",
      "address": "123 Main St",
      "city": "New York",
      "country": "USA"
    },
    "education": [
      {
        "degree": "B.S. in Computer Science",
        "institution": "Stanford University",
        "start_date": "2008",
        "end_date": "2012",
        "result": ["3.8/4.0 GPA"]
      }
    ],
    "work_experience": [
      {
        "job_title": "Software Engineer",
        "company": "TechCorp",
        "dates": "2012-2022",
        "responsibilities": ["Developed web applications", "Led agile teams"],
        "achievements": ["Increased user engagement by 30%"]
      }
    ],
    "skills": {
      "technical": ["Python", "JavaScript", "AWS", "Docker"],
      "professional": ["Leadership", "Agile", "Communication"]
    },
    "projects": [],
    "publications": [],
    "certifications": [],
    "awards": [],
    "references": [],
    "hobbies": []
  },
  "job_title": "Senior Software Engineer",
  "job_description": "We are seeking a Senior Software Engineer with 5+ years of experience in Python, cloud technologies (AWS/Azure), and containerization (Docker/Kubernetes). The ideal candidate will have strong leadership skills, experience with agile methodologies, and a proven track record of building scalable applications. Bachelor's degree in Computer Science or related field required."
}
```

**Request Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| cv_data | object | Yes | Structured CV data (follows CV_STRUCTURE_SCHEMA) |
| job_title | string | Yes | Target job position |
| job_description | string | Yes | Full job description text |

**Response:**
```json
{
  "overall_score": 82.5,
  "overall_feedback": "Strong candidate with excellent technical background and relevant experience. The CV demonstrates solid alignment with the job requirements, particularly in Python, AWS, and agile methodologies. Minor improvements needed in highlighting containerization experience and advanced cloud architecture expertise.",
  "section_feedbacks": [
    {
      "section_name": "personal_info",
      "score": 95.0,
      "feedback": "Complete and professional contact information with LinkedIn profile.",
      "strengths": [
        "All required contact details present",
        "Professional LinkedIn profile included"
      ],
      "improvements": [
        "Consider adding a professional website or portfolio link"
      ]
    },
    {
      "section_name": "education",
      "score": 90.0,
      "feedback": "Strong educational background from a prestigious institution with excellent GPA.",
      "strengths": [
        "Relevant degree in Computer Science",
        "High GPA demonstrates academic excellence",
        "Graduated from top-tier university"
      ],
      "improvements": [
        "Could mention relevant coursework or academic projects"
      ]
    },
    {
      "section_name": "work_experience",
      "score": 85.0,
      "feedback": "Solid 10-year experience with relevant technical work. Good demonstration of leadership and impact.",
      "strengths": [
        "Meets experience requirement (5+ years)",
        "Shows leadership experience",
        "Quantifiable achievements present"
      ],
      "improvements": [
        "Add more details about cloud architecture experience",
        "Highlight specific containerization projects",
        "Include more metrics and quantifiable results"
      ]
    },
    {
      "section_name": "skills",
      "score": 80.0,
      "feedback": "Good match with required skills including Python, AWS, and Agile. Missing some advanced cloud technologies.",
      "strengths": [
        "Python expertise matches requirement",
        "AWS cloud experience present",
        "Docker containerization mentioned",
        "Agile methodology experience"
      ],
      "improvements": [
        "Add Kubernetes experience if applicable",
        "Include specific AWS services used",
        "Mention CI/CD tools and practices"
      ]
    },
    {
      "section_name": "certifications",
      "score": 60.0,
      "feedback": "No certifications listed. AWS or cloud certifications would strengthen the application.",
      "strengths": [],
      "improvements": [
        "Consider obtaining AWS Certified Solutions Architect",
        "Add any relevant professional certifications",
        "Include training courses or bootcamps completed"
      ]
    }
  ],
  "keyword_match_percentage": 75.5,
  "recommendations": [
    "Add Kubernetes experience to skills section to better match job requirements",
    "Obtain AWS certification to strengthen cloud expertise credentials",
    "Expand work experience descriptions with more specific cloud architecture examples",
    "Include metrics and quantifiable achievements in all work experiences",
    "Add a projects section showcasing relevant technical work",
    "Mention specific AWS services (EC2, S3, Lambda, etc.) used in previous roles"
  ]
}
```

**Scoring System:**
| Score Range | Rating | Description |
|-------------|--------|-------------|
| 90-100 | Excellent | Highly qualified, exceptional match |
| 75-89 | Good | Qualified with minor gaps |
| 60-74 | Moderate | Some relevant experience, notable gaps |
| 40-59 | Weak | Significant skill/experience gaps |
| 0-39 | Poor | Not qualified for the position |

**Section Feedbacks:**
Each CV section is analyzed individually with:
- **section_name**: CV section being evaluated
- **score**: Section-specific score (0-100)
- **feedback**: Overall assessment of the section
- **strengths**: Positive aspects identified
- **improvements**: Specific actionable suggestions

---

## Error Handling

All endpoints return standard HTTP error responses:

**400 Bad Request:**
```json
{
  "detail": "Only PDF files are supported"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating summary: <error message>"
}
```

---

## Rate Limiting & Performance

- All endpoints use Groq's LLaMA 3.3 70B model
- Average response time: 1-5 seconds depending on complexity
- Temperature varies by endpoint for optimal results:
  - CV Summary: 0.2-0.5 (randomized)
  - Responsibilities: 0.2-0.5 (randomized)
  - Skills: 0.2-0.5 (randomized)
  - CV Structure: 0.5 (fixed)
  - ATS Score: 0.3 (fixed for consistency)

---

## Notes

- All text outputs are cleaned to remove harmful special characters
- PDF parsing supports multi-page resumes
- Skills are returned in a formatted string with single quotes
- Responsibilities are newline-separated for easy parsing
- ATS scoring considers keyword matching, experience relevance, and completeness
- Temperature is included in responses for transparency and reproducibility

---