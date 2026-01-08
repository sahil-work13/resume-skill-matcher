🚀 AI Resume & Career Assistant

An end-to-end AI-powered Resume Analysis & Career Assistant platform that allows users to upload resumes and job descriptions, analyze compatibility, and interact with their documents using an LLM-powered chatbot.

This system supports multi-document context, session-aware chat memory, document-based Q&A, and production-grade AI deployment using FastAPI + Hugging Face + Django.

📌 Key Features
📄 Resume & Job Description Analysis

Upload Resume (PDF/DOCX) and Job Description

Extract:

Skills

Experience

Education

Role & Seniority

Calculate:

Skill match score

ATS compatibility score

Requirement coverage

Role fit score

🤖 AI Career Chatbot (Llama-3 Powered)

Ask questions directly from uploaded documents

Examples:

“Summarize my skills”

“What job roles fit my profile?”

“Rewrite my experience section”

Strict document grounding (no hallucination)

ChatGPT-style structured responses with:

Headings

Bullet points

Emojis

Clear formatting

📂 Multi-Document Support

Upload multiple PDFs / DOCX files per chat

No re-upload required for every question

Session-aware document memory

🧠 Chat History & Sessions

Each conversation saved as a Chat Session

Sidebar history

Rename / Delete chats

Resume conversation anytime

⚡ Streaming AI Responses

Token-by-token streaming (ChatGPT-like typing)

Faster perceived response time

Professional UX

📊 ATS & Recruiter Insights

ATS scorecard

Keyword gap detection

Recruiter-style feedback

Improvement suggestions

📥 Report Generation

Download analysis reports in:

PDF

DOCX

🏗️ System Architecture
Frontend (HTML / JS / CSS)
        |
        |  Fetch API (Streaming)
        ↓
Django Backend (Auth, Sessions, Storage)
        |
        | HTTP Request
        ↓
FastAPI AI Service (HuggingFace Space)
        |
        | Llama-3 Inference
        ↓
AI Response Stream → User Interface

🧰 Tech Stack
🔹 Frontend

HTML5

CSS3

Vanilla JavaScript

Fetch API (Streaming)

Marked.js (Markdown rendering)

🔹 Backend (Main App)

Django

Django Auth (Login Required)

Django Sessions

Django ORM

REST APIs (JSON)

🔹 AI Service

FastAPI

HuggingFace Inference Client

Meta LLaMA-3 (8B Instruct)

StreamingResponse

🔹 AI / NLP Tools

LangChain (Document loading)

PDF / DOCX parsers

Skill extraction logic

Context builders

Prompt engineering

🔹 Deployment

Hugging Face Spaces (FastAPI AI)

Environment variables (HF_TOKEN)

Uvicorn ASGI server

🔐 Authentication & Security

User authentication required for:

Chatbot

Resume upload

Chat history

Each user has isolated chat sessions

Document context is never shared across users

Prompt injection protection:

Strict document-only answering

No assumptions allowed

🧠 AI Prompt Strategy
System Prompt Rules

Answer only from provided documents

No assumptions or hallucinations

Clear fallback:

“The document does not contain this information.”

Response Style

Markdown formatted

ChatGPT-style structure

Headings, bullet points, emojis

Recruiter-friendly answers

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

🔁 Request Flow (Chatbot)

User uploads resume / documents

Text extracted & stored in session

User asks a question

Django:

Builds system prompt

Appends document context

Sends request to FastAPI

FastAPI:

Streams response from LLaMA-3

Django:

Forwards stream

Frontend:

Displays streaming answer

Renders Markdown

🧪 Example Queries

“Summarize my technical skills”

“What job roles fit me best?”

“What are my educational qualifications?”

“Which skills am I missing for a backend role?”

“Rewrite my experience section professionally”

🚀 Future Enhancements

Vector embeddings (FAISS / Chroma)

Semantic document search

Chat export (PDF)

Resume rewriting mode

Job recommendation engine

Admin analytics dashboard

Real-time WebSocket streaming

👨‍💻 Author

Sahil Koshti
Aspiring Full-Stack & AI Engineer
📧 Email: sahilkoshti1354@gmail.com

⭐ Why This Project Stands Out

Production-grade AI architecture

Clean separation of concerns

Real LLM deployment (not mock)

Strong prompt safety

Recruiter-ready outputs

Scalable design
