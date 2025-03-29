from django.urls import path
from ares import views
from rest_framework import routers
router = routers.DefaultRouter()

urlpatterns = [
    path(r'constraints/', views.handleConstraints.as_view(), name='constraints'),
]