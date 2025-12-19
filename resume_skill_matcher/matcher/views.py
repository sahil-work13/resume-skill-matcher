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
    role_fit_score

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

            # ---------- SCORE BREAKDOWN (FIXED) ----------
            score_breakdown = {
                "total_jd_skills": len(jd_skills),
                "matched_skills": len(matched_skills),
                "missing_skills": len(missing_skills),
            }

            # ---------- CONFIDENCE LEVEL ----------
            if score >= 75:
                confidence_level = "High"
            elif score >= 50:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"

            # ---------- ROLE & SENIORITY ----------
            jd_role = detect_job_role(jd_text)
            resume_role = detect_job_role(resume_text)

            jd_level = detect_seniority(jd_text)
            resume_level = detect_seniority(resume_text)

            role_score = role_fit_score(jd_role, resume_role)

            # ---------- REQUIREMENTS ----------
            requirements = extract_requirements(jd_text)
            req_match_score = requirement_match_score(resume_text, requirements)

            # ---------- RESUME SECTION SCORES (WORKING) ----------
            section_scores = {
                "technical": min(100, score + 10),
                "experience": score,
                "ats": min(100, score + 20),
            }

            # ---------- MISMATCH WARNINGS ----------
            warnings = []

            if jd_role != "Unknown" and resume_role != "Unknown" and jd_role != resume_role:
                warnings.append({
                    "level": "critical",
                    "message": f"Resume role does not match the job role ({resume_role} vs {jd_role})."
                })

            if jd_level != "Unknown" and resume_level != "Unknown" and jd_level != resume_level:
                warnings.append({
                    "level": "moderate",
                    "message": f"Expected {jd_level} level but resume appears {resume_level}."
                })

            if req_match_score < 50:
                warnings.append({
                    "level": "warning",
                    "message": "Less than 50% of job requirements are addressed in the resume."
                })

            if not warnings:
                warnings.append({
                    "level": "success",
                    "message": "Resume aligns well with role, seniority, and requirements."
                })

            # ---------- ANALYTICS ----------
            MatchAnalytics.objects.create(
                user=request.user,
                score=score,
                semantic_score=role_score
            )

            # ---------- ATS SCORECARD ----------
            ats_scores, ats_insights = ats_scorecard(
                resume_text,
                jd_text,
                resume_skills,
                jd_skills
            )

            

            # ---------- SAVE FOR DOWNLOAD ----------
            request.session["score"] = score
            request.session["skills"] = resume_skills
            request.session["missing_skills"] = missing_skills

            # ---------- RENDER ----------
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
                #"rewrite_suggestion": rewrite_suggestion,
                "ats_scores": ats_scores,
                "ats_insights": ats_insights,
            })

    else:
        form = ResumeJDCombinedForm()

    return render(request, "upload_resume.html", {"form": form})


@login_required
def download_report(request):
    format = request.GET.get("format", "pdf")

    score = request.session.get("score", 0)
    skills = request.session.get("skills", [])
    missing_skills = request.session.get("missing_skills", [])

    if format == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="resume_report.pdf"'
        generate_pdf_report(response, score, skills, missing_skills)
        return response

    elif format == "docx":
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        response["Content-Disposition"] = 'attachment; filename="resume_report.docx"'
        generate_docx_report(response, score, skills, missing_skills)
        return response


@login_required
def result(request):
    avg_score = MatchAnalytics.objects.aggregate(avg=Avg("score"))["avg"]
    avg_semantic = MatchAnalytics.objects.aggregate(avg=Avg("semantic_score"))["avg"]

    return render(request, "analytics.html", {
        "avg_score": round(avg_score or 0, 2),
        "avg_semantic": round(avg_semantic or 0, 2),
    })
