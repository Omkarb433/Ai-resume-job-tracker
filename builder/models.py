from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="profile")
    full_name = models.CharField(max_length=120)
    title = models.CharField(max_length=120, blank=True)
    summary = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)


    def __str__(self):
        return self.full_name


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.degree} at {self.school}"   

class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=255, default="Unknown Role")
    company = models.CharField(max_length=255, default="Unknown Company")
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(default=timezone.now)  # required, with safe default
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} at {self.company}"


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)       # optional
    description = models.TextField(blank=True, null=True)                 # optional
    link = models.URLField(blank=True, null=True)                         # optional
    tech_stack = models.CharField(max_length=255, blank=True, null=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else "Untitled Project"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=200, blank=True)
    objective = models.TextField(blank=True)
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_generated = models.DateTimeField(blank=True, null=True)

class JobPosting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    company = models.CharField(max_length=160)
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_date = models.DateTimeField(default=timezone.now)
    apply_deadline = models.DateTimeField(default=timezone.now) 

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    ats_score = models.FloatField(default=0)
    match_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)  # ✅ allow null + blank

    def __str__(self):
        return f"{self.name} - {self.issuer}"




class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    programming_languages = models.CharField(max_length=200, blank=True)
    frameworks = models.CharField(max_length=200, blank=True)
    databases = models.CharField(max_length=200, blank=True)
    tools = models.CharField(max_length=200, blank=True)
    soft_skills = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username}'s skills"
