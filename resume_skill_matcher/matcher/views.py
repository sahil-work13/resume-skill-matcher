from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Avg
from django.http import JsonResponse
import json  
import requests

from .models import Resume, JobDescription, MatchAnalytics , ChatMessage , ChatSession
from .forms import ResumeJDCombinedForm
from .utils import (
    extract_text_from_file,
    extract_skills,     
    calculate_match_score,
    ats_scorecard,
    detect_job_role,
    detect_seniority,
    extract_requirements,
    requirement_match_score,
    role_fit_score,
    recruiter_resume_feedback,
    build_system_prompt,
    
)
import logging
logger = logging.getLogger(__name__)
from .reports.pdf_report import generate_pdf_report
from .reports.docx_report import generate_docx_report
from chatbot.context_builder import build_resume_context
from chatbot.document_loader import load_document
from chatbot.chatbot_engine import get_chatbot
from chatbot.file_utils import save_file


@login_required
def upload_resume_and_jd(request):

    if request.method == "POST":
        form = ResumeJDCombinedForm(request.POST, request.FILES)

        if form.is_valid():

            # ---------- RESUME ----------
            resume = Resume.objects.create(
                user=request.user,
                resume_file=form.cleaned_data["resume_file"]
            )

            resume_text = extract_text_from_file(resume.resume_file.path)
            resume.extracted_text = resume_text
            resume.save()

            resume_skills = extract_skills(resume_text)
            

            # ---------- JOB DESCRIPTION ----------
            jd = JobDescription.objects.create(
                jd_file=form.cleaned_data["jd_file"]
            )

            jd_text = extract_text_from_file(jd.jd_file.path)
            jd.extracted_text = jd_text
            jd.save()

            jd_skills = extract_skills(jd_text)

            # ---------- SKILL MATCH ----------
            matched_skills = list(set(resume_skills) & set(jd_skills))
            missing_skills = list(set(jd_skills) - set(resume_skills))
            score = calculate_match_score(resume_skills, jd_skills)

            score_breakdown = {
                "total_jd_skills": len(jd_skills),
                "matched_skills": len(matched_skills),
                "missing_skills": len(missing_skills),
            }

            confidence_level = (
                "High" if score >= 75 else
                "Medium" if score >= 50 else
                "Low"
            )

            # ---------- ROLE & LEVEL ----------
            jd_role = detect_job_role(jd_text)
            resume_role = detect_job_role(resume_text)

            jd_level = detect_seniority(jd_text)
            resume_level = detect_seniority(resume_text)

            role_score = role_fit_score(jd_role, resume_role)

            # ---------- REQUIREMENTS ----------
            requirements = extract_requirements(jd_text)
            req_match_score = requirement_match_score(resume_text, requirements)

            # ---------- SECTION SCORES ----------
            section_scores = {
                "technical": min(100, score + 10),
                "experience": score,
                "ats": min(100, score + 20),
            }

            # ---------- WARNINGS ----------
            warnings = []

            if jd_role != resume_role:
                warnings.append({
                    "level": "critical",
                    "message": f"Resume role does not match JD role ({resume_role} vs {jd_role})."
                })

            if jd_level != resume_level:
                warnings.append({
                    "level": "moderate",
                    "message": f"Expected {jd_level} level but resume appears {resume_level}."
                })

            if req_match_score < 50:
                warnings.append({
                    "level": "warning",
                    "message": "Less than 50% of job requirements are covered."
                })

            if not warnings:
                warnings.append({
                    "level": "success",
                    "message": "Resume aligns well with the job description."
                })

            # ---------- ATS SCORE ----------
            ats_scores, ats_insights = ats_scorecard(
                resume_text, jd_text, resume_skills, jd_skills
            )

            # ---------- AI FEEDBACK ----------
            recruiter_feedback = recruiter_resume_feedback(resume_text, jd_text)
            if not recruiter_feedback:
                recruiter_feedback = (
                    "Resume is relevant but can improve keyword alignment, impact statements, "
                    "and clarity for better recruiter appeal."
                )

            # ---------- SAVE SESSION ----------
            request.session["score"] = score
            request.session["skills"] = resume_skills
            request.session["missing_skills"] = missing_skills

            # ---------- SAVE SESSION FOR CHATBOT ----------
            request.session["resume_analysis"] = {
                "skills": resume_skills,  # This is a list of strings
                "experience": resume_text[:3000], # Give it more text to read
                "education": "Included in resume",
                "ats_score": ats_scores.get('overall', 0),
                "role": resume_role
            }
            # This line is crucial for the Greeting to work!
            request.session["user_display_name"] = request.user.get_full_name() or request.user.username
            

            #--------REPORT CALL---------

            report_context = {
                "score": score,
                "confidence_level": confidence_level,
                "skills": resume_skills,
                "missing_skills": missing_skills,
                "score_breakdown": score_breakdown,
                "section_scores": section_scores,
                "jd_role": jd_role,
                "resume_role": resume_role,
                "role_fit_score": role_score,
                "jd_level": jd_level,
                "resume_level": resume_level,
                "requirements": requirements,
                "requirement_match_score": req_match_score,
                "warnings": warnings,
                "ats_scores": ats_scores,
                "ats_insights": ats_insights,
                "recruiter_feedback": recruiter_feedback,
                
            }
            request.session["report_context"] = report_context


            # ---------- RENDER RESULT ----------
            return render(request, "result.html", {
                "score": score,
                "confidence_level": confidence_level,
                "skills": resume_skills,
                "missing_skills": missing_skills,
                "score_breakdown": score_breakdown,
                "section_scores": section_scores,
                "jd_role": jd_role,
                "resume_role": resume_role,
                "role_fit_score": role_score,
                "jd_level": jd_level,
                "resume_level": resume_level,
                "requirements": requirements,
                "requirement_match_score": req_match_score,
                "warnings": warnings,
                "ats_scores": ats_scores,
                "ats_insights": ats_insights,
                "recruiter_feedback": recruiter_feedback,
            })

    else:
        form = ResumeJDCombinedForm()

    return render(request, "upload_resume.html", {"form": form})



@login_required
def download_report(request):
    format = request.GET.get("format", "pdf")
    context = request.session.get("report_context")

    if not context:
        return HttpResponse("No report data found.", status=400)

    if format == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="resume_report.pdf"'
        generate_pdf_report(response, context)
        return response

    elif format == "docx":
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = 'attachment; filename="resume_report.docx"'
        generate_docx_report(response, context)
        return response


@login_required
def result(request):
    avg_score = MatchAnalytics.objects.aggregate(avg=Avg("score"))["avg"]
    avg_semantic = MatchAnalytics.objects.aggregate(avg=Avg("semantic_score"))["avg"]

    return render(request, "analytics.html", {
        "avg_score": round(avg_score or 0, 2),
        "avg_semantic": round(avg_semantic or 0, 2),
    })

@login_required
def resume_chatbot_page(request):
    """Renders the interface and greets the user by name."""
    # We pull the data from the session that was set during the initial upload
    context = {
        "user_display_name": request.session.get("user_display_name", "Candidate"),
        "resume_analysis": request.session.get("resume_analysis", {"role": "Professional"})
    }
    return render(request, "chatbot_interface.html", context)


@login_required
def resume_chatbot_api(request):

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_query = data.get("question")
    session_id = data.get("session_id")

    if not user_query:
        return JsonResponse({"error": "Empty question"}, status=400)

    # =========================
    # A️⃣ HANDLE CHAT SESSION
    # =========================
    if not session_id:
        session = ChatSession.objects.create(
            user=request.user,
            title=user_query[:30] + "..."
        )
        session_id = session.id
    else:
        session = ChatSession.objects.get(id=session_id, user=request.user)

    # =========================
    # B️⃣ SAVE USER MESSAGE
    # =========================
    ChatMessage.objects.create(
        session=session,
        sender="user",
        content=user_query
    )

    # =========================
    # C️⃣ BUILD DOCUMENT CONTEXT
    # =========================
    extra_context = request.session.get("extra_context", "")

    # 🔐 HARD LIMIT to avoid HF 500 errors
    MAX_CHARS = 6000   # ~4k tokens safe
    if len(extra_context) > MAX_CHARS:
        extra_context = extra_context[-MAX_CHARS:]


    system_prompt = (
        "You are a professional career assistant.\n"
        "Answer STRICTLY from the provided document content.\n"
        "If the answer is not present, say:\n"
        "'The document does not contain this information.'"
    )

    final_prompt = f"""
DOCUMENT CONTENT:
----------------
{extra_context}

USER QUESTION:
--------------
{user_query}
"""

    # =========================
    # D️⃣ CALL FASTAPI (HF)
    # =========================
    fastapi_url = "https://sk1354-llama3-career-api.hf.space/chat"

    payload = {
        "prompt": final_prompt,
        "system_prompt": system_prompt,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            fastapi_url,
            json=payload,
            timeout=90
        )

        print("FASTAPI STATUS:", response.status_code)
        print("FASTAPI TEXT:", response.text)

        resp_json = response.json()

        if response.status_code == 200 and "answer" in resp_json:
            bot_answer = resp_json["answer"]
        else:
            bot_answer = f"AI error: {resp_json}"

    except Exception as e:
        print("FASTAPI CALL FAILED:", str(e))
        bot_answer = "Sorry, I couldn't reach the AI server."

    # =========================
    # E️⃣ SAVE BOT MESSAGE
    # =========================
    ChatMessage.objects.create(
        session=session,
        sender="bot",
        content=bot_answer
    )

    return JsonResponse({
        "answer": bot_answer,
        "session_id": session_id,
        "new_title": session.title
    })


    
@login_required
def chatbot_upload_extra_file(request):
    print("--- DEBUG: upload_extra_file triggered ---")

    if request.method != "POST":
        return JsonResponse({"message": "Invalid request method."}, status=400)

    uploaded_files = request.FILES.getlist("files")
    print(f"DEBUG: Number of files received: {len(uploaded_files)}")

    if not uploaded_files:
        return JsonResponse({"message": "No files uploaded."}, status=400)

    try:
        combined_content = ""
        file_names = []

        for f in uploaded_files:
            print(f"DEBUG: Processing file: {f.name}")
            path = save_file(f)
            docs = load_document(path)
            content = " ".join([doc.page_content for doc in docs])

            combined_content += f"\n--- Document: {f.name} ---\n{content}\n"
            file_names.append(f.name)

        current_extra = request.session.get("extra_context", "")
        request.session["extra_context"] = current_extra + combined_content
        request.session.modified = True

        print("DEBUG SUCCESS: Files processed and session updated.")

        return JsonResponse({
            "message": f"Successfully processed: {', '.join(file_names)}"
        })

    except Exception as e:
        print("DEBUG EXCEPTION:", str(e))
        return JsonResponse({"message": str(e)}, status=500)

# 1. API to Get Sidebar History
@login_required
def get_chat_history(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    data = [{"id": s.id, "title": s.title} for s in sessions]
    return JsonResponse(data, safe=False)

# 2. API to Load Specific Conversation
@login_required
def get_session_messages(request, session_id):
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        messages = session.messages.all()
        data = [{"sender": m.sender, "content": m.content} for m in messages]
        return JsonResponse({"status": "ok", "messages": data})
    except ChatSession.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Chat not found"}, status=404)
    

@login_required
def rename_chat(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        new_title = data.get("title")
        if not new_title:
            return JsonResponse({"error": "Title required"}, status=400)

        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.title = new_title
        session.save()

        return JsonResponse({"status": "ok"})
    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)

@login_required
def delete_chat(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.delete()
        return JsonResponse({"status": "deleted"})
    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)
