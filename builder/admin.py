from django.contrib import admin
from .models import UserProfile, Education, Experience, Project, Resume, JobPosting, Application
admin.site.register([UserProfile ,Education, Experience, Project, Resume, JobPosting, Application])

