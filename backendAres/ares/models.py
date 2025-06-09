from django.db import models
from behave.parser import Parser
from django.contrib.auth.models import AbstractUser, Group, Permission

class Lesson(models.Model):
    short_name = models.CharField(max_length=255)
    activity_type_name = models.CharField(max_length=255)
    semester = models.IntegerField()
    department = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255, blank=True, null=True)
    grp = models.CharField(max_length=255, blank=True, null=True)
    teacher = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'lessons'

class Audience(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    floor = models.IntegerField()
    building = models.CharField(max_length=100)

    class Meta:
        db_table = 'audience'
        
    def __str__(self):
        return f"{self.building} {self.name} (этаж {self.floor})"
    
class User_stuff(AbstractUser):
    stuff_id = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",
        related_query_name="custom_user_group",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="custom_user_permission",
    )

    def __str__(self):
        return self.username


class Constraints(models.Model):
    name = models.TextField(primary_key=True)
    content = models.TextField()
    faculty = models.CharField(max_length=20, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=20, blank=True, null=True)

    def parse_content(self):
        parser = Parser()
        if not self.content.strip().startswith("# language:"):
            content_with_language = f"# language: ru\nФункция: {self.name}\n\n{self.content}"
        else:
            content_with_language = self.content

        feature = parser.parse(content_with_language)
        parsed_data = []

        for scenario in feature.scenarios:
            steps = []
            for step in scenario.steps:
                steps.append({
                    "keyword": step.keyword.strip(),
                    "text": step.name.strip()
                })

            parsed_data.append({
                "scenario_name": scenario.name.strip(),
                "steps": steps
            })

        return parsed_data
    
    class Meta:
        db_table = 'constraints'

    def __str__(self):
        return self.name