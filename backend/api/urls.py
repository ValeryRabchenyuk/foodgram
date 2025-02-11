from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipesViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipesViewSet, basename='recipe')

api_urls = [path('', include(router.urls)), ]

auth_urls = [path('', include('djoser.urls.authtoken'))]

urlpatterns = [
    path('', include(api_urls)),
    path('auth/', include(auth_urls))
]
