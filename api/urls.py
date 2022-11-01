from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'bot_users', TgUserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'posts', PostViewSet)
router.register(r'favourites', FavouriteRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
