from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Avg

from .models import Resume, JobDescription, MatchAnalytics
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
    rewrite_resume_bullets,
    generate_skill_roadmap,
    skill_gap_score,
    generate_mock_interview_questions,
    ats_keyword_suggestions
)
from .reports.pdf_report import generate_pdf_report
from .reports.docx_report import generate_docx_report


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

            rewrite_suggestions = rewrite_resume_bullets(resume_text, jd_text)
            skill_roadmap = generate_skill_roadmap(missing_skills)
            skill_gap = skill_gap_score(resume_text, jd_text)
            mock_interview = generate_mock_interview_questions(resume_text, jd_text)
            ats_keywords = ats_keyword_suggestions(resume_text, jd_text)

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
                "rewrite_suggestions": rewrite_suggestions,
                "skill_roadmap": skill_roadmap,
                "skill_gap": skill_gap,
                "mock_interview": mock_interview,
                "ats_keywords": ats_keywords,
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
