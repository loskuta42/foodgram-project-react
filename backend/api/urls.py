from django.urls import include, path, re_path
from rest_framework import routers

from .views import (CartView, DownloadCart, FavoriteView, IngredientViewSet,
                    RecipeViewSet, TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='Tag')
router.register('ingredients', IngredientViewSet, basename='Ingredient')
router.register('recipes', RecipeViewSet, basename='Recipe')

urlpatterns = [
    re_path(
        r'recipes/(?P<recipe_id>[0-9]+)/favorite/',
        FavoriteView.as_view(),
        name='Favorite'
    ),
    re_path(
        r'recipes/(?P<recipe_id>[0-9]+)/shopping_cart/',
        CartView.as_view(),
        name='Cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadCart.as_view(),
        name='DownloadCart'
    ),
    path('', include(router.urls))
]
