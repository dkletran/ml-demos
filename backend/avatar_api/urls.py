from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api', views.AvatarStylingApiViewSet, basename='api')

urlpatterns = router.urls