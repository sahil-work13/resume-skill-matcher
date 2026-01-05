from django.urls import path
from .views import upload_resume_and_jd,result,download_report,resume_chatbot_api,resume_chatbot_page,chatbot_upload_extra_file,get_chat_history,get_session_messages,rename_chat,delete_chat

urlpatterns = [
    path("", upload_resume_and_jd, name="upload_resume"),
    path("result/", result, name="result"),
    path("download-report/", download_report, name="download_report"),
    path('chatbot/', resume_chatbot_page, name='resume_chatbot_page'),
    path('chatbot/api/',resume_chatbot_api, name='resume_chatbot_api'),
    path('api/upload/', chatbot_upload_extra_file, name='chatbot_upload_extra'),
    path('api/history/', get_chat_history, name='chat_history'),
    path('api/history/<int:session_id>/', get_session_messages, name='session_messages'),
    path("api/chat/<int:session_id>/rename/", rename_chat),
    path("api/chat/<int:session_id>/delete/", delete_chat),
]
