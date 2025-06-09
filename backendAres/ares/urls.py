from django.urls import path
from ares import views
from rest_framework import routers
router = routers.DefaultRouter()

urlpatterns = [
    path(r'constraints/', views.HandleConstraints.as_view(), name='constraints'),
    path(r'constraints/<str:name>/', views.HandleConstraints.as_view(), name='constraint-detail'),
    path(r'auth/oauth/', views.OAuthCallbackView.as_view(), name='oauth'),
    path(r'teachers/', views.UniqueTeachersView.as_view(), name='teachers'),
    path(r'audiences/', views.AudienceListView.as_view(), name='audiences'),
    path(r'buildings/', views.UniqueBuildingsView.as_view(), name='buildings'),
    path(r'lessons/', views.LessonListView.as_view(), name='lessons')
]