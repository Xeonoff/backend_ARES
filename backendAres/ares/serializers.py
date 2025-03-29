from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from ares import models
from collections import OrderedDict

class constraintSerializer(serializers.ModelSerializer):
    parsed_content = serializers.SerializerMethodField()

    class Meta:
        model = models.Constraints
        fields = ['name', 'content', 'parsed_content', 'faculty', 'semester', 'building', 'department']

    def get_parsed_content(self, obj):
        """
        Возвращает результат парсинга content.
        """
        return obj.parse_content()
