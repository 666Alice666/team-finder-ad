from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project, Skill


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными пользователями, проектами и навыками."

    def handle(self, *args, **options):
        User = get_user_model()

        users = {item["email"]: self.create_user(User, item) for item in self.user_rows()}
        projects = [self.create_project(row, users) for row in self.project_rows()]
        projects[0].participants.add(users["lev.teamfinder@example.com"])
        projects[1].participants.add(users["maria@yandex.ru"])

        self.stdout.write(self.style.SUCCESS("Демонстрационные данные TeamFinder готовы."))

    def create_user(self, User, row):
        fields = row.copy()
        password = fields.pop("password")
        user, created = User.objects.update_or_create(email=fields["email"], defaults=fields)
        if created or not user.has_usable_password():
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def create_project(self, row, users):
        project_fields = row.copy()
        owner_email = project_fields.pop("owner_email")
        skill_names = project_fields.pop("skills")
        project, _ = Project.objects.update_or_create(
            owner=users[owner_email],
            name=project_fields["name"],
            defaults={**project_fields, "owner": users[owner_email]},
        )
        project.participants.add(users[owner_email])
        project.skills.set(self.get_skills(skill_names))
        return project

    def get_skills(self, names):
        return [Skill.objects.get_or_create(name=name)[0] for name in names]

    def user_rows(self):
        return (
            {
                "email": "maria@yandex.ru",
                "password": "password",
                "name": "Мария",
                "surname": "Новикова",
                "phone": "+79001002030",
                "about": "Пишу API на Django и ищу небольшую команду для полезного сервиса.",
                "github_url": "https://github.com/maria-teamfinder",
            },
            {
                "email": "lev.teamfinder@example.com",
                "password": "password",
                "name": "Лев",
                "surname": "Орлов",
                "phone": "+79001002031",
                "about": "Frontend-разработчик. Люблю понятные интерфейсы и быстрые прототипы.",
                "github_url": "https://github.com/lev-orlov",
            },
            {
                "email": "dina.teamfinder@example.com",
                "password": "password",
                "name": "Дина",
                "surname": "Соколова",
                "phone": "+79001002032",
                "about": "Дизайнер интерфейсов, собираю команду для образовательных продуктов.",
                "github_url": "",
            },
            {
                "email": "timur.teamfinder@example.com",
                "password": "password",
                "name": "Тимур",
                "surname": "Валеев",
                "phone": "+79001002033",
                "about": "DevOps-инженер, помогаю pet-проектам быстрее доезжать до продакшена.",
                "github_url": "https://github.com/timur-devops",
            },
        )

    def project_rows(self):
        return (
            {
                "owner_email": "maria@yandex.ru",
                "name": "Карта волонтёрских задач",
                "description": "Сервис, где НКО публикуют небольшие задачи, а волонтёры быстро находят посильную помощь рядом с собой.",
                "github_url": "https://github.com/maria-teamfinder/volunteer-map",
                "skills": ("Django", "PostgreSQL", "Leaflet"),
            },
            {
                "owner_email": "lev.teamfinder@example.com",
                "name": "Трекер привычек для учебных групп",
                "description": "Командный трекер прогресса: участники отмечают занятия, видят серию дней и поддерживают друг друга.",
                "github_url": "https://github.com/lev-orlov/study-habits",
                "skills": ("React", "TypeScript", "REST API"),
            },
            {
                "owner_email": "dina.teamfinder@example.com",
                "name": "Библиотека дизайн-разборов",
                "description": "Площадка для коротких разборов интерфейсов с тегами, примерами и обсуждением решений.",
                "github_url": "",
                "skills": ("Figma", "UX Research", "HTML"),
            },
            {
                "owner_email": "timur.teamfinder@example.com",
                "name": "Шаблон деплоя Django-проектов",
                "description": "Набор Docker Compose конфигураций и инструкций для быстрого запуска учебных Django-приложений.",
                "github_url": "https://github.com/timur-devops/django-launch-kit",
                "skills": ("Docker", "Nginx", "PostgreSQL"),
            },
        )

