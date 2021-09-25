from django.contrib import admin

from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Страница тэгов в админке."""

    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Страница тэгов в админке."""

    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Страница рецептов в админке."""

    list_display = (
        'pk',
        'author',
        'name',
        'text',
        'image',
        'cooking_time',
        'pub_date',
        'is_favorited',
        'ingredients',
        'tags',
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return obj.favorites.count()

    def ingredients(self, obj):
        return list(obj.ingredients.all())

    def tags(self, obj):
        return list(obj.tags.all())


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Страница ингредиентов в рецепте."""

    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe',)
    list_filter = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Страница избранных рецептов."""

    list_display = (
        'pk',
        'owner',
        'recipe'
    )
    search_fields = ('owner', 'recipe')
    list_filter = ('owner', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Страница списка покупок."""

    list_display = (
        'pk',
        'owner',
        'recipe'
    )
    search_fields = ('owner', 'recipe')
    list_filter = ('owner', 'recipe')
    empty_value_display = '-пусто-'
