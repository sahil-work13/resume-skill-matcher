import os
import uuid
from django.conf import settings

def save_file(uploaded_file):
    upload_dir = os.path.join(settings.MEDIA_ROOT, "chatbot_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Unique filename to avoid collisions
    file_ext = uploaded_file.name.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"

    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path
