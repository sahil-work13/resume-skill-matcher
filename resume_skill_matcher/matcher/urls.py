from django.urls import path
from .views import upload_resume_and_jd,result,download_report

urlpatterns = [
    path("upload/", upload_resume_and_jd, name="upload_resume"),
    path("result/", result, name="result"),
    path("download-report/", download_report, name="download_report"),
]
