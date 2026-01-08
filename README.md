🚀 AI Resume & Career Assistant

An end-to-end AI-powered Resume Analysis & Career Assistant that helps users analyze resumes, match them with job descriptions, and interact with their documents using an LLM-powered chatbot.

The platform supports multi-document understanding, session-aware chat memory, document-grounded Q&A, and production-grade AI deployment using Django, FastAPI, and Hugging Face (LLaMA-3).

✨ What This Project Does (In Simple Terms)

Upload your resume and job description

Get ATS score, skill match, and recruiter insights

Chat with your resume like ChatGPT

Ask questions directly from your documents

Download detailed PDF / DOCX reports

All chats are saved and can be resumed anytime

📌 Key Features
📄 Resume & Job Description Analysis

Upload Resume (PDF / DOCX) and Job Description

Automatically extract:

Skills

Experience

Education

Role & seniority level

Calculate:

Skill match score

ATS compatibility score

Requirement coverage

Role fit score

🤖 AI Career Chatbot (LLaMA-3 Powered)

Ask questions directly from uploaded documents

Example queries:

“Summarize my skills”

“What job roles fit my profile?”

“Rewrite my experience section professionally”

Strict document grounding

No hallucinations

No assumptions

ChatGPT-style responses with:

Clear headings

Bullet points

Emojis

Clean formatting

📂 Multi-Document Support

Upload multiple PDFs / DOCX files in one chat

Ask multiple questions without re-uploading

Session-aware document memory

🧠 Chat History & Sessions

Each conversation is saved as a chat session

Sidebar chat history

Rename or delete chats

Resume conversations anytime

⚡ Streaming AI Responses

Token-by-token streaming (ChatGPT-like typing)

Faster and more natural interaction

Professional user experience

📊 ATS & Recruiter Insights

ATS scorecard

Keyword gap detection

Recruiter-style feedback

Actionable improvement suggestions

📥 Report Generation

Download analysis reports in:

PDF

DOCX

🏗️ System Architecture
Frontend (HTML / CSS / JavaScript)
        |
        | Fetch API (Streaming)
        ↓
Django Backend (Auth, Sessions, Storage)
        |
        | HTTP API Call
        ↓
FastAPI AI Service (Hugging Face Space)
        |
        | LLaMA-3 Inference
        ↓
Streaming AI Response → User Interface

🧰 Tech Stack
🔹 Frontend

HTML5

CSS3

Vanilla JavaScript

Fetch API (Streaming)

Marked.js (Markdown rendering)

🔹 Backend (Main Application)

Django

Django Authentication (Login Required)

Django Sessions

Django ORM

REST APIs (JSON)

🔹 AI Service

FastAPI

Hugging Face Inference Client

Meta LLaMA-3 (8B Instruct)

StreamingResponse (real-time output)

🔹 AI / NLP Tools

LangChain (document loading)

PDF & DOCX parsers

Skill extraction logic

Context builders

Advanced prompt engineering

🔹 Deployment

Hugging Face Spaces (FastAPI AI service)

Environment variables (HF_TOKEN)

Uvicorn ASGI server

🔐 Authentication & Security

Login required for:

Chatbot access

Resume upload

Chat history

Each user has isolated chat sessions

Uploaded document context is never shared

Prompt injection protection:

Answers only from documents

No assumptions or fabricated data

🧠 AI Prompt Strategy
System Prompt Rules

Answer only from the provided documents

No assumptions or hallucinations

Fallback message:

“The document does not contain this information.”

Response Style

Markdown formatted

ChatGPT-style structure

Headings, bullet points, emojis

Recruiter-friendly and easy to scan

📁 Project Structure (Simplified)
project/
│
├── chatbot/
│   ├── document_loader.py
│   ├── context_builder.py
│   ├── chatbot_engine.py
│   └── file_utils.py
│
├── resumes/
│   ├── models.py
│   ├── views.py
│   ├── utils.py
│   └── reports/
│
├── templates/
│   ├── upload_resume.html
│   ├── result.html
│   └── chatbot_interface.html
│
├── fastapi_app/
│   └── app.py
│
└── README.md

🔁 Chatbot Request Flow

User uploads resume / documents

Text is extracted and stored in session

User asks a question

Django:

Builds system prompt

Appends document context

Sends request to FastAPI

FastAPI:

Streams response from LLaMA-3

Django:

Forwards the stream

Frontend:

Displays live typing

Renders Markdown

🧪 Example Questions

“Summarize my technical skills”

“What job roles fit me best?”

“What is my educational background?”

“Which skills am I missing for a backend role?”

“Rewrite my experience section professionally”

🚀 Future Enhancements

Vector embeddings (FAISS / ChromaDB)

Semantic document search

Chat export (PDF)

Resume rewriting mode

Job recommendation engine

Admin analytics dashboard

WebSocket-based real-time streaming

👨‍💻 Author

Sahil Koshti
Aspiring Full-Stack & AI Engineer
📧 Email: sahilkoshti1354@gmail.com

⭐ Why This Project Stands Out

Production-grade AI architecture

Real LLM deployment (no mock APIs)

Strong prompt safety & grounding

Clean separation of concerns

Recruiter-ready outputs

Scalable and extensible design
