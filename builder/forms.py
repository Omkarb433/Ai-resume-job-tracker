from django import forms
from .models import UserProfile, Education, Experience, Project, Certification
from .models import UserSkill
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import JobPosting, Application




class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "full_name", "title", "summary", "email", "phone",
            "location", "linkedin", "github", "profile_pic"
        ]
class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ["role", "company", "location", "start_date", "end_date", "description"]
        widgets = {
            "role": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Software Engineer"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Google"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mumbai"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Describe your work"}),
        }

        
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "tech_stack", "description", "link"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Online Resume Builder"}),
            "tech_stack": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Django, Bootstrap, SQLite"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Briefly describe the project", "rows": 3}),
            "link": forms.URLInput(attrs={"class": "form-control", "placeholder": "e.g. https://github.com/username/project"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Explicitly mark optional fields
        self.fields["title"].required = False
        self.fields["description"].required = False
        self.fields["tech_stack"].required = False
        self.fields["link"].required = False

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["school", "degree", "field_of_study", "start_date", "end_date", "grade", "description"]
        widgets = {
            "school": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. University of Mumbai"}),
            "degree": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Bachelor of Engineering"}),
            "field_of_study": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Computer Science"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "grade": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 8.5 CGPA"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Details about your studies"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False  # all optional

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuer', 'issue_date', 'expiry_date', 'credential_url']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }



class UserSkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = [
            "programming_languages",
            "frameworks",
            "databases",
            "tools",
            "soft_skills",
        ]
        widgets = {
            "programming_languages": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Python, JavaScript, C++"
            }),
            "frameworks": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Django, React, Bootstrap"
            }),
            "databases": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. MySQL, PostgreSQL, MongoDB"
            }),
            "tools": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Git, Docker, AWS"
            }),
            "soft_skills": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Problem Solving, Communication, Teamwork"
            }),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label="Upload Resume",
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.docx,.txt"})
    )

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ["title", "company", "location", "description", "url", "apply_deadline"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "apply_deadline": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }