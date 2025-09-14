from email.mime import text
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import login
from io import BytesIO 
from urllib3 import request
from xhtml2pdf import pisa

from .models import (
    UserProfile, Education, Experience, Project, Certification, Resume,
    JobPosting, Application, UserSkill
)
from .forms import (
    ProfileForm, EducationForm, ExperienceForm, ProjectForm,
    CertificationForm, UserSkillForm, CustomUserCreationForm, ResumeUploadForm
)
from .services.ai import improve_text_service
from .services.ats import ats_score
from .services.match import match_score
from .utils import extract_text, parse_resume
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import JobPosting, Application
from .forms import JobPostingForm





def _get_resume_text(user):
    profile = UserProfile.objects.filter(user=user).first()
    exps = Experience.objects.filter(user=user)
    skills = UserSkill.objects.filter(user=user).first()
    edus = Education.objects.filter(user=user)
    projs = Project.objects.filter(user=user)

    blocks = []

    # Profile
    if profile:
        blocks.append(f"{profile.full_name or ''} {profile.title or ''} {profile.summary or ''}")

    # Experience
    for e in exps:
        blocks.append(f"{e.role or ''} {e.company or ''} {e.description or ''}")

    # Skills
    if skills:
        for field in ['programming_languages', 'frameworks', 'databases', 'tools', 'soft_skills']:
            value = getattr(skills, field, "")
            if value:
                blocks.append(value)

    # Education
    for edu in edus:
        blocks.append(f"{edu.degree or ''} {edu.school or ''} {edu.field_of_study or ''} {edu.grade or ''}")

    # Projects
    for p in projs:
        blocks.append(f"{p.title or ''} {p.description or ''} {p.tech_stack or ''}")

    return "\n".join([b.strip() for b in blocks if b.strip()])

@login_required(login_url='/accounts/login/')
def dashboard(request):
    jobs = JobPosting.objects.filter(user=request.user).order_by('-created_at')[:10]
    profile = UserProfile.objects.filter(user=request.user).first()
    return render(request, 'builder/dashboard.html', {"jobs": jobs, "profile": profile})

def new_job(request):
    return render(request, "builder/new_job.html")

def job_score(request, job_id):
    return render(request, "builder/job_score.html")

def experience_view(request):
    return render(request, 'builder/experience.html')

def skill_view(request):
    return render(request, 'builder/skill.html')

def project_view(request):
    return render(request, 'builder/project.html')

def education_view(request):
    return render(request, 'builder/education.html')

def certification_view(request):
    return render(request, 'builder/certification.html')

def upload_resume(request):
    return render(request, 'builder/upload_resume.html')

def edit_full_profile(request):
    # Create formsets
    EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=1, can_delete=True)
    ExperienceFormSet = modelformset_factory(Experience, form=ExperienceForm, extra=1, can_delete=True)
    SkillFormSet = modelformset_factory(UserSkill, form=UserSkillForm, extra=1, can_delete=True)
    ProjectFormSet = modelformset_factory(Project, form=ProjectForm, extra=1, can_delete=True)
    CertificationFormSet = modelformset_factory(Certification, form=CertificationForm, extra=1, can_delete=True)

    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        edu_formset = EducationFormSet(request.POST, queryset=Education.objects.filter(user=request.user))
        exp_formset = ExperienceFormSet(request.POST, queryset=Experience.objects.filter(user=request.user))
        skill_formset = SkillFormSet(request.POST, queryset=UserSkill.objects.filter(user=request.user))
        proj_formset = ProjectFormSet(request.POST, queryset=Project.objects.filter(user=request.user))
        cert_formset = CertificationFormSet(request.POST, queryset=Certification.objects.filter(user=request.user))

        if (profile_form.is_valid() and edu_formset.is_valid() and exp_formset.is_valid() 
            and skill_formset.is_valid() and proj_formset.is_valid() and cert_formset.is_valid()):
            
            profile_form.save()

            # Save formsets with user
            for formset in [edu_formset, exp_formset, skill_formset, proj_formset, cert_formset]:
                objects = formset.save(commit=False)
                for obj in objects:
                    obj.user = request.user
                    obj.save()
                for obj in formset.deleted_objects:
                    obj.delete()

            return redirect("profile")  # redirect to profile page after save

    else:
        profile_form = ProfileForm(instance=profile)
        edu_formset = EducationFormSet(queryset=Education.objects.filter(user=request.user))
        exp_formset = ExperienceFormSet(queryset=Experience.objects.filter(user=request.user))
        skill_formset = SkillFormSet(queryset=UserSkill.objects.filter(user=request.user))
        proj_formset = ProjectFormSet(queryset=Project.objects.filter(user=request.user))
        cert_formset = CertificationFormSet(queryset=Certification.objects.filter(user=request.user))

    return render(request, "builder/edit_full_profile.html", {
        "profile_form": profile_form,
        "edu_formset": edu_formset,
        "exp_formset": exp_formset,
        "skill_formset": skill_formset,
        "proj_formset": proj_formset,
        "cert_formset": cert_formset,
    })



def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create empty profile linked to user
            UserProfile.objects.create(
                user=user,
                full_name=user.username,
                email=user.email
            )
            login(request, user)
            return redirect("edit_profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "builder/register.html", {"form": form})


def login_register(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()

    if request.method == "POST":
        if "password1" in request.POST:  # Register form
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                auth_login(request, user)
                return redirect("dashboard")
        else:  # Login form
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                auth_login(request, user)
                return redirect("dashboard")

    return render(request, "builder/auth_base.html", {
        "login_form": login_form,
        "register_form": register_form,
    })



@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("upload_resume")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "builder/edit_profile.html", {"form": form, "step": 1, "total_steps": 7})


@login_required
def upload_resume(request):
    form = ResumeUploadForm()  # Define the form variable
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        if resume_file:
            # Save or update user's resume
            resume, created = Resume.objects.get_or_create(user=request.user)
            resume.file = resume_file
            resume.save()
        # Redirect to next step in flow
        return redirect("skills")  # next step: skills
    return render(request, "builder/upload_resume.html", {"form": form, "step": 2, "total_steps": 7})

@login_required
def skill_view(request):
    skills, _ = UserSkill.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserSkillForm(request.POST, instance=skills)
        if form.is_valid():
            form.save()
            return redirect("experience")  # go to next step
    else:
        form = UserSkillForm(instance=skills)
    return render(request, "builder/skill.html", {"form": form, "step": 3, "total_steps": 7})
@login_required
def experience_view(request):
    """Show all experiences + form"""
    experiences = Experience.objects.filter(user=request.user)
    form = ExperienceForm()
    return render(request, "builder/experience.html", {"experiences": experiences, "form": form})


@login_required
def save_experience(request):
    """Save a single experience per form submit"""
    if request.method == "POST":
        action = request.POST.get("action")
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, "Experience saved successfully!")

            if action == "continue":
                return redirect("education")  # ✅ Save & Continue button
            return redirect("experience")
        else:
            messages.error(request, "Please correct the errors below.")

    return redirect("experience")


@login_required
def edit_experience(request, pk):
    """
    Edit an existing experience.
    Supports:
    - Updating experience
    - Deleting experience
    - Save & Continue (redirect to next step, e.g., certifications)
    """
    experience = get_object_or_404(Experience, pk=pk, user=request.user)
    
    if request.method == "POST":
        if "delete" in request.POST:
            experience.delete()
            messages.success(request, "Experience deleted successfully!")
            return redirect("experience")  # Redirect to experience list page

        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Experience updated successfully!")

            if request.POST.get("action") == "continue":
                return redirect("certification")  # Redirect to next step
            return redirect("experience")  # Stay on experience list

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExperienceForm(instance=experience)

    return render(request, "builder/edit_experience.html", {"form": form, "experience": experience})

@login_required
def delete_experience(request, pk):
    exp = get_object_or_404(Experience, pk=pk, user=request.user)
    if request.method == "POST":
        exp.delete()
        messages.success(request, "Experience deleted successfully!")
    return redirect("experience")



@login_required
def project_view(request):
    """Show all projects + form"""
    projects = Project.objects.filter(user=request.user)
    return render(request, "builder/project.html", {"projects": projects})

@login_required
def save_project(request):
    """Save a single project per form submit"""
    if request.method == "POST":
        action = request.POST.get("action")

        title = request.POST.get("title", "").strip()
        tech_stack = request.POST.get("tech_stack", "").strip()
        description = request.POST.get("description", "").strip()
        link = request.POST.get("link", "").strip()

        if action == "add":
            # ✅ Don’t force title required
            if not (title or tech_stack or description or link):
                messages.warning(request, "Empty project not saved.")
                return redirect("project")

            Project.objects.create(
                user=request.user,
                title=title,
                tech_stack=tech_stack,
                description=description,
                link=link
            )
            messages.success(request, "Project added successfully!")
            return redirect("project")

        elif action == "continue":
            messages.success(request, "Redirecting to next step...")
            return redirect("education")

    return redirect("project")


@login_required
def edit_project(request, pk):
    """Edit an existing project"""
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == "POST":
        project.title = request.POST.get("title", project.title)
        project.tech_stack = request.POST.get("tech_stack", project.tech_stack)
        project.description = request.POST.get("description", project.description)
        project.link = request.POST.get("link", project.link)
        project.save()

        messages.success(request, "Project updated successfully!")
        return redirect("project")  # ✅ FIX: redirect back to main projects page

    return render(request, "builder/edit_project.html", {"project": project})


@login_required
def delete_project(request, pk):
    """Delete a project"""
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("project")
    return redirect("project")


@login_required
def education_view(request):
    """Show form + saved educations"""
    educations = Education.objects.filter(user=request.user).order_by('-created_at')

    if request.method == "POST":
        action = request.POST.get("action")
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = request.user
            edu.save()
            messages.success(request, "Education saved successfully!")

            if action == "continue":
                return redirect("certification")
            return redirect("education")
    else:
        form = EducationForm()

    return render(request, "builder/education.html", {"form": form, "educations": educations})

@login_required
def save_education(request):
    """Save a single education entry"""
    if request.method == "POST":
        action = request.POST.get("action")

        school = request.POST.get("school", "").strip()
        degree = request.POST.get("degree", "").strip()
        field_of_study = request.POST.get("field_of_study", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        grade = request.POST.get("grade", "").strip()
        description = request.POST.get("description", "").strip()

        if action == "add":
            if not (school or degree or field_of_study):
                messages.warning(request, "Empty education not saved.")
                return redirect("education")

            Education.objects.create(
                user=request.user,
                school=school,
                degree=degree,
                field_of_study=field_of_study,
                start_date=start_date or None,
                end_date=end_date or None,
                grade=grade,
                description=description,
            )
            messages.success(request, "Education added successfully!")
            return redirect("education")

        elif action == "continue":
            messages.success(request, "Redirecting to next step...")
            return redirect("certification")

    return redirect("education")


@login_required
def edit_education(request, pk):
    """Edit an existing education"""
    education = get_object_or_404(Education, pk=pk, user=request.user)

    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education updated successfully!")
            return redirect("education")
    else:
        form = EducationForm(instance=education)

    return render(request, "builder/education_edit.html", {"form": form, "education": education})


@login_required
def delete_education(request, pk):
    """Delete an education entry"""
    education = get_object_or_404(Education, pk=pk, user=request.user)
    if request.method == "POST":
        education.delete()
        messages.success(request, "Education deleted successfully!")
    return redirect("education")


def certification_view(request):
    certifications = Certification.objects.filter(user=request.user)
    return render(request, "builder/certification.html", {"certifications": certifications})

@login_required
def save_certifications(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Get form data
        name = request.POST.get("name", "").strip()
        issuer = request.POST.get("issuer", "").strip()
        issue_date = request.POST.get("issue_date", "").strip()
        expiry_date = request.POST.get("expiry_date", "").strip()
        credential_url = request.POST.get("credential_url", "").strip()

        if action == "add":
            # Validate only for "+ Add Certificate"
            if not name or not issue_date:
                messages.error(request, "Certificate Name and Issue Date are required.")
                return redirect("certification")
            
            # Save certificate
            Certification.objects.create(
                user=request.user,
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                expiry_date=expiry_date or None,
                credential_url=credential_url,
            )
            messages.success(request, "Certificate added successfully!")
            return redirect("certification")  # stay on page to add more

        elif action == "continue":
            # Skip validation, go straight to profile
            messages.success(request, "Redirecting to profile...")
            return redirect("profile")

    # fallback GET request
    return redirect("certification")

@login_required
def edit_certification(request, pk):
    certification = get_object_or_404(Certification, pk=pk, user=request.user)

    if request.method == 'POST':
        certification.name = request.POST.get("name", certification.name)
        certification.issuer = request.POST.get("issuer", certification.issuer)
        certification.issue_date = request.POST.get("issue_date", certification.issue_date)
        certification.expiry_date = request.POST.get("expiry_date", certification.expiry_date)
        certification.credential_url = request.POST.get("credential_url", certification.credential_url)
        certification.save()
        messages.success(request, "Certification updated successfully!")
        return redirect("certification")

    return render(request, "builder/edit_certification.html", {"certification": certification})


def delete_certification(request, pk):
    certification = get_object_or_404(Certification, pk=pk, user=request.user)
    if request.method == "POST":
        certification.delete()
        messages.success(request, "Certification deleted successfully!")
        return redirect("certification")
    return redirect("certification")


@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)
    skills = UserSkill.objects.filter(user=request.user)
    experiences = Experience.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    education = Education.objects.filter(user=request.user)
    certifications = Certification.objects.filter(user=request.user)

    return render(request, "builder/profile.html", {
        "profile": profile,
        "skills": skills,
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "certifications": certifications,
    })


@login_required
def create_job(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        description = request.POST.get('description')
        job = JobPosting.objects.create(
            user=request.user,   # 👈 link with logged-in user
            title=title,
            company=company,
            description=description
        )
        return redirect('score_job', job_id=job.id)
    return render(request, 'builder/job_new.html')

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, user=request.user)
    if request.method == "POST":
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("dashboard")
    else:
        form = JobPostingForm(instance=job)
    return render(request, "builder/edit_job.html", {"form": form})


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, user=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect("dashboard")
    return render(request, "builder/delete_job.html", {"job": job})

@login_required
def score_job(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)

    # Get resume text
    resume_text = _get_resume_text(request.user)

    # Calculate scores
    ats = ats_score(resume_text, job.description)
    match = match_score(resume_text, job.description)

    # Save or update application (avoid duplicates)
    app, created = Application.objects.update_or_create(
        user=request.user,
        job=job,
        defaults={"ats_score": ats, "match_score": match},
    )

    return render(request, "builder/score.html", {
        "job": job,
        "application": app,
        "created": created,  # optional: tells if it's new or updated
    })

@login_required
def resume_pdf(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    skills = UserSkill.objects.filter(user=request.user).first()  # ✅ Fix here
    experiences = Experience.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    education = Education.objects.filter(user=request.user)
    certifications = Certification.objects.filter(user=request.user)

    html = render_to_string("builder/resume_pdf.html", {
        "profile": profile,
        "skills": skills,  # ✅ now it's a single object
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "certifications": certifications,
    })

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)

    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resume.pdf"'
    return response



@login_required
def improve_text_view(request):
    print("improve_text_view called")

    improved = None
    original_text = None

    if request.method == "POST":
        original_text = request.POST.get("text", "").strip()
        prompt = request.POST.get(
            "prompt", "Rewrite to be concise, action-focused, and ATS-friendly."
        ).strip()

        if not original_text:
            return render(request, "builder/improve.html", {
                "error": "⚠️ Please provide some text to improve."
            })

        # Call helper service
        improved = improve_text_service(original_text, prompt)

    return render(
        request,
        "builder/improve.html",
        {
            "original_text": original_text,
            "improved_text": improved,
        },
    )



@login_required
def profile(request):
    return render(request, 'builder/profile.html')




