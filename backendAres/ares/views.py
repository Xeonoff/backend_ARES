from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
        
        # Фильтрация по параметрам
        filters = {
            'name__icontains': self.request.query_params.get('name'),
            'faculty': self.request.query_params.get('faculty'),
            'semester': self.request.query_params.get('semester'),
            'building': self.request.query_params.get('building'),
            'department': self.request.query_params.get('department'),
        }
        
        # Собираем условия фильтрации
        filter_kwargs = {k: v for k, v in filters.items() if v is not None}
        
        # Обрабатываем числовое поле
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