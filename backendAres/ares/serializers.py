from rest_framework import serializers
from ares import models

class ConstraintSerializer(serializers.ModelSerializer):
    parsed_content = serializers.SerializerMethodField()

    class Meta:
        model = models.Constraints
        fields = [
            'name', 
            'content', 
            'parsed_content', 
            'faculty', 
            'semester', 
            'building', 
            'department'
        ]
        extra_kwargs = {
            'name': {'validators': []}
        }

    def get_parsed_content(self, obj):
        return obj.parse_content()

    def validate_content(self, value):
        try:
            temp_constraint = models.Constraints(content=value)
            temp_constraint.parse_content()
            return value
        except Exception as e:
            raise serializers.ValidationError(
                f"Ошибка парсинга контента: {str(e)}"
            )

    def create(self, validated_data):
        name = validated_data.get('name')
        if models.Constraints.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {'name': 'Правило с таким именем уже существует'}
            )
            
        return super().create(validated_data)