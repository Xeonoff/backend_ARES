from django.db import models
from behave.parser import Parser

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