from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Min
import requests
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from ares import models, serializers

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100
    page_query_param = 'page'

class HandleConstraints(APIView):
    pagination_class = CustomPagination
    
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class() if self.pagination_class else None
        return self._paginator
    
    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, self) if self.paginator else None
    
    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)
    def get_queryset(self):
        queryset = models.Constraints.objects.all()

        filters = {
            'name__icontains': self.request.query_params.get('name'),
            'faculty': self.request.query_params.get('faculty'),
            'semester': self.request.query_params.get('semester'),
            'building': self.request.query_params.get('building'),
            'department': self.request.query_params.get('department'),
        }

        filter_kwargs = {k: v for k, v in filters.items() if v is not None}

        if 'semester' in filter_kwargs:
            try:
                filter_kwargs['semester'] = int(filter_kwargs['semester'])
            except ValueError:
                raise ValidationError({'semester': 'Must be an integer'})
        
        return queryset.filter(**filter_kwargs)

    def get(self, request, name=None, format=None, *args, **kwargs):
        queryset = self.get_queryset()
        if name:
            constraint = get_object_or_404(models.Constraints, name=name)
            serializer = serializers.ConstraintSerializer(constraint)
            return Response(serializer.data)
        
        constraints = models.Constraints.objects.all()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ConstraintSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = serializers.ConstraintSerializer(constraints, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.ConstraintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, name, format=None):
        constraint = get_object_or_404(models.Constraints, name=name)
        serializer = serializers.ConstraintSerializer(
            constraint, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OAuthCallbackView(APIView):
    def post(self, request):
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        token_response = requests.post(
            f"https://science.iu5.bmstu.ru/sso/token?code={code}"
        )

        if token_response.status_code != 200:
            return Response({'error': 'Invalid authorization code'}, status=400)

        access_token = token_response.json().get('access_token')

        user_response = requests.get(
            f"https://science.iu5.bmstu.ru/sso/person?access_token={access_token}"
        )

        if user_response.status_code != 200:
            return Response({'error': 'Failed to fetch user data'}, status=400)

        user_data = user_response.json()

        user, _ = models.User_stuff.objects.update_or_create(
            username=user_data['username'],
            defaults={
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'is_staff': user_data.get('is_staff', False)
            }
        )

        return Response({
            'access_token': access_token,
            'user': {
                'id': user.stuff_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff
            }
        })
    
class AudienceListView(APIView):
    def get(self, request):
        building_filter = request.query_params.get('building', None)
        floor_filter = request.query_params.get('floor', None)

        queryset = models.Audience.objects.all()

        if building_filter:
            queryset = queryset.filter(building__icontains=building_filter)
        
        if floor_filter:
            try:
                floor_value = int(floor_filter)
                queryset = queryset.filter(floor=floor_value)
            except ValueError:
                return Response({"error": "Floor must be an integer"}, status=400)
        
        min_ids = queryset.values('name').annotate(min_id=Min('id')).values_list('min_id', flat=True)

        unique_queryset = queryset.filter(id__in=min_ids)

        result = [
            {
                "id": aud.id,
                "name": aud.name,
                "floor": aud.floor,
                "building": aud.building
            }
            for aud in unique_queryset
        ]
        
        return Response(result)

class UniqueTeachersView(APIView):
    def get(self, request):
        teachers = models.Lesson.objects.exclude(teacher__isnull=True).exclude(teacher='') \
                                .order_by('teacher') \
                                .distinct('teacher') \
                                .values_list('teacher', flat=True)
                                
        return Response(list(teachers))

class UniqueBuildingsView(APIView):
    def get(self, request):
        buildings = models.Audience.objects.order_by('building') \
                                   .values_list('building', flat=True) \
                                   .distinct()

        building_list = list(buildings)
        
        return Response(building_list)

class LessonListView(APIView):
    def get(self, request):
        lessons = models.Lesson.objects.all()
        result = [
            {
                "short_name" : lesson.short_name,
                "activity_type_name" : lesson.activity_type_name,
                "semester" : lesson.semester,
                "department" : lesson.department,
                "faculty" : lesson.faculty,
                "grp" : lesson.grp,
                "teacher" : lesson.teacher
            }
            for lesson in lessons
        ]
        return Response(result)