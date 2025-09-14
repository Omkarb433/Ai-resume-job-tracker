from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from .views import save_project, delete_project, edit_project, project_view
from django.conf import settings
from django.conf.urls.static import static
from builder import views as builder_views


def devtools_ignore(request):
    return JsonResponse({}, status=204)  # Empty response
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('jobs/new/', views.create_job, name='create_job'),
    path('jobs/<int:job_id>/score/', views.score_job, name='score_job'),
    path("jobs/new/", views.new_job, name="new_job"),  
    path("jobs/<int:job_id>/score/", views.job_score, name="job_score"),
    path('experience/', views.experience_view, name='experience'),
    path("resume/", views.upload_resume, name="upload_resume"),
    path('skill/', views.skill_view, name='skills'),
    path('project/', views.project_view, name='project'),
    path('education/', views.education_view, name='education'),
    path('certification/', views.certification_view, name='certification'),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("login/", auth_views.LoginView.as_view(template_name="builder/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", views.register, name="register"),
    path("resume_pdf/", views.resume_pdf, name="resume_pdf"),
    path("auth/", views.login_register, name="login_register"),
    path(".well-known/appspecific/com.chrome.devtools.json", devtools_ignore),
    path('profile/upload_resume/', views.upload_resume, name='upload_resume'),
    path("resume/", views.upload_resume, name="upload_resume"),
    path('profile/upload_resume/', views.upload_resume, name='upload_resume'),
    path("projects/", project_view, name="project"),
    path("projects/save/", save_project, name="save_project"),
    path("projects/<int:pk>/edit/", edit_project, name="edit_project"),
    path("projects/<int:pk>/delete/", delete_project, name="delete_project"),
    path('education/', views.education_view, name='education'),
    path('profile/', views.profile, name='profile'),
    path("certification/", views.certification_view, name="certification"),
    path("save-certifications/", views.save_certifications, name="save_certifications"),
    path("certification/edit/<int:pk>/", views.edit_certification, name="edit_certification"),
    path("certification/delete/<int:pk>/", views.delete_certification, name="delete_certification"),
    path('certifications/save/', views.save_certifications, name='save_certifications'),
    path("improve/", views.improve_text_view, name="improve_text"),
    path("jobs/<int:job_id>/edit/", views.edit_job, name="edit_job"),
    path("jobs/<int:job_id>/delete/", views.delete_job, name="delete_job"),
    path("jobs/<int:pk>/score/", views.job_score, name="job_score"),
    path("education/", views.education_view, name="education"),
    path("education/save/", views.save_education, name="save_education"),
    path("education/<int:pk>/edit/", views.edit_education, name="edit_education"),
    path("education/<int:pk>/delete/", views.delete_education, name="delete_education"),
    path("education/<int:pk>/edit/", views.edit_education, name="edit_education"),
    path("education/<int:pk>/delete/", views.delete_education, name="delete_education"),
    path("experience/", views.experience_view, name="experience"),
    path("experience/save/", views.save_experience, name="save_experience"),
    path("experience/<int:pk>/edit/", views.edit_experience, name="edit_experience"),
    path("experience/<int:pk>/delete/", views.delete_experience, name="delete_experience"),
   



]

# Serving media files during development
if settings.DEBUG:  # only in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)