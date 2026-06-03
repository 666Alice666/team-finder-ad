import json

from django.core.exceptions import ValidationError

from .models import Project, Skill


def get_request_payload(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST


def project_feed(active_skill=None):
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    return projects


def project_with_public_details():
    return Project.objects.select_related("owner").prefetch_related("participants", "skills")


def available_skill_names():
    return Skill.objects.order_by("name").values_list("name", flat=True)


def save_new_project(form, owner):
    project = form.save(commit=False)
    project.owner = owner
    project.save()
    project.participants.add(owner)
    return project


def user_can_manage_project(user, project):
    return user.is_authenticated and (project.owner_id == user.id or user.is_staff)


def close_project(project, user):
    if not user_can_manage_project(user, project) or not project.is_open:
        return False

    project.status = Project.CLOSED
    project.save(update_fields=["status"])
    return True


def switch_participation(project, user):
    already_joined = project.participants.filter(pk=user.pk).exists()
    relation_action = project.participants.remove if already_joined else project.participants.add
    relation_action(user)
    return not already_joined


def autocomplete_skills(query, limit):
    skills = Skill.objects.order_by("name")
    if query:
        skills = skills.filter(name__istartswith=query.strip())
    return skills.values("id", "name")[:limit]


def normalize_skill_name(value):
    return " ".join((value or "").split())


def get_or_create_skill_by_name(name):
    normalized_name = normalize_skill_name(name)
    if not normalized_name:
        raise ValidationError("Название навыка не может быть пустым.")

    skill = Skill.objects.filter(name__iexact=normalized_name).first()
    if skill:
        return skill, False

    return Skill.objects.create(name=normalized_name), True


def resolve_skill_from_payload(payload):
    skill_id = payload.get("skill_id")
    if skill_id:
        skill = Skill.objects.filter(pk=skill_id).first()
        if skill is None:
            raise ValidationError("Выбранный навык не найден.")
        return skill, False
    return get_or_create_skill_by_name(payload.get("name"))


def attach_skill(project, skill):
    was_attached = project.skills.filter(pk=skill.pk).exists()
    if not was_attached:
        project.skills.add(skill)
    return not was_attached


def detach_skill(project, skill):
    if not project.skills.filter(pk=skill.pk).exists():
        return False
    project.skills.remove(skill)
    return True


def serialize_skill_relation(skill, created, added):
    return {
        "id": skill.id,
        "name": skill.name,
        "skill_id": skill.id,
        "created": created,
        "added": added,
    }
