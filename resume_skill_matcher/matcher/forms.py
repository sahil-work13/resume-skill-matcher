from django import forms

class ResumeJDCombinedForm(forms.Form):
    resume_file = forms.FileField(label="Resume")
    jd_file = forms.FileField(label="Job Description")
