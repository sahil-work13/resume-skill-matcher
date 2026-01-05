import os
import sys

path = '/home/sahil-work13/resume-skill-matcher'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'resume_skill_matcher.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
