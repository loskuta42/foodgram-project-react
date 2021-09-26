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
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


class IngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


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
        'get_ingredients',
        'get_tags',
    )
    inlines = (
        IngredientsInline,
    )
    search_fields = ('name', 'author__email', 'author__username')
    list_filter = ('author', 'tags')
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return obj.fav_recipes.count()

    def get_ingredients(self, obj):
        return "\n".join([ing.name for ing in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])

    get_tags.short_description = 'Теги'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Страница ингредиентов в рецепте."""

    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = (
        'recipe',
        'ingredient__measurement_unit'
    )
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Страница избранных рецептов."""

    list_display = (
        'pk',
        'owner',
        'recipe'
    )
    search_fields = (
        'owner__email',
        'recipe__name',
    )
    list_filter = ('recipe__tags',)
    empty_value_display = '-пусто-'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Страница списка покупок."""

    list_display = (
        'pk',
        'owner',
        'recipe'
    )
    search_fields = ('owner__email', 'recipe__name')
    list_filter = ('recipe__tags',)
    empty_value_display = '-пусто-'
