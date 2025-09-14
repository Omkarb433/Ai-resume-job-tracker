from django.contrib import admin
from django.urls import path, include
from builder import views as builder_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", builder_views.dashboard, name="dashboard"),
    path("profile/", builder_views.edit_profile, name="edit_profile"),
    path("jobs/new/", builder_views.create_job, name="create_job"),
    path("jobs/<int:job_id>/score/", builder_views.score_job, name="score_job"),
    path("resume/pdf/", builder_views.resume_pdf, name="resume_pdf"),
    path("improve/", builder_views.improve_text_view, name="improve_text"),

    path("", include("builder.urls")),

    # ✅ Add this line
    path("accounts/", include("django.contrib.auth.urls")),
    
]
 
 