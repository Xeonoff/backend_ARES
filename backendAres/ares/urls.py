from django.urls import path
from ares import views
from rest_framework import routers
router = routers.DefaultRouter()

urlpatterns = [
    path(r'constraints/', views.HandleConstraints.as_view(), name='constraints'),
    path(r'constraints/<str:name>/', views.HandleConstraints.as_view(), name='constraint-detail'),
]