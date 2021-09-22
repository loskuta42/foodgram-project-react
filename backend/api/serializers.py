from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import CustomUserSerializer

from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер ингредиентов в рецептах."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления/обновления рецепта."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            owner=cur_user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return Cart.objects.filter(
            owner=cur_user,
            recipe=obj
        ).exists()


class PreviewRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер предпросмотра рецепта."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = obj.image.url
        return request.build_absolute_uri(image_url)


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер добавления/обновления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return Favorite.objects.filter(owner=cur_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        return Cart.objects.filter(owner=cur_user, recipe=obj).exists()

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        print(ingredients)
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingr_obj = ingredient['ingredient']
            # ingr_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            amount = ingredient['amount']
            if RecipeIngredient.objects.filter(
                    recipe=recipe,
                    ingredient=ingr_obj
            ).exists():
                amount += F('amount')
            RecipeIngredient.objects.update_or_create(
                defaults={'amount': amount},
                recipe=recipe,
                ingredient=ingr_obj,
            )
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredients:
                ingr_obj = ingredient['ingredient']
                # ingr_obj = get_object_or_404(Ingredient, id=ingredient['id'])
                amount = ingredient['amount']
                if RecipeIngredient.objects.filter(
                        recipe=instance,
                        ingredient=ingr_obj
                ).exists():
                    amount += F('amount')
                RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingr_obj,
                    defaults={'amount': amount}
                )

        instance.name = validated_data.get(
            'name',
            instance.name
        )
        instance.text = validated_data.get(
            'text',
            instance.text
        )
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        cooking_time = self.initial_data.get('cooking_time')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'ingredients': ('Количество ингредиетнта'
                                    ' должно быть больше нуля.')
                })
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': ('Время приготовления '
                                 'должно быть больше нуля')
            })
        return data

    def to_representation(self, instance):
        recipes = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return recipes.data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('owner', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('owner', 'recipe'),
                message='Рецепт уже в находиться в избранном'
            )
        ]

    def to_representation(self, instance):
        recipes = PreviewRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        )
        return recipes.data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('owner', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('owner', 'recipe'),
                message='Рецепт уже в находиться в корзине.'
            )
        ]

    def to_representation(self, instance):
        print(instance)
        recipes = PreviewRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        )
        return recipes.data
