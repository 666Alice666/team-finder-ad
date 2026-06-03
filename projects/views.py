from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from common.constants import PROJECTS_PER_PAGE, SKILLS_AUTOCOMPLETE_LIMIT
from common.services import get_query_prefix, paginate_queryset

from .forms import ProjectForm
from .models import Project
from .services import (
    attach_skill,
    autocomplete_skills,
    available_skill_names,
    close_project,
    detach_skill,
    get_request_payload,
    project_feed,
    project_with_public_details,
    resolve_skill_from_payload,
    save_new_project,
    serialize_skill_relation,
    switch_participation,
    user_can_manage_project,
)


def project_list(request):
    active_skill = request.GET.get("skill")
    projects_page = paginate_queryset(request, project_feed(active_skill), PROJECTS_PER_PAGE)
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects_page,
            "page_obj": projects_page,
            "all_skills": available_skill_names(),
            "active_skill": active_skill,
            "query_prefix": get_query_prefix(request),
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(project_with_public_details(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = save_new_project(form, request.user)
        return redirect("projects:project_detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not user_can_manage_project(request.user, project):
        return redirect("projects:project_detail", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if not close_project(project, request.user):
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    return JsonResponse({"status": "ok", "project_status": Project.CLOSED})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return JsonResponse(
        {"status": "ok", "participant": switch_participation(project, request.user)}
    )


@require_GET
def skill_suggestions(request):
    return JsonResponse(
        list(autocomplete_skills(request.GET.get("q", ""), SKILLS_AUTOCOMPLETE_LIMIT)),
        safe=False,
    )


@login_required
@require_POST
def add_project_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not user_can_manage_project(request.user, project):
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    try:
        skill, created = resolve_skill_from_payload(get_request_payload(request))
    except ValidationError as error:
        return JsonResponse(
            {"status": "error", "errors": error.messages},
            status=HTTPStatus.BAD_REQUEST,
        )

    return JsonResponse(
        serialize_skill_relation(skill, created, attach_skill(project, skill))
    )


@login_required
@require_POST
def remove_project_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if not user_can_manage_project(request.user, project):
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    skill = get_object_or_404(Skill, pk=skill_id)
    if not detach_skill(project, skill):
        return JsonResponse({"status": "error"}, status=HTTPStatus.NOT_FOUND)

    return JsonResponse({"status": "ok"})

