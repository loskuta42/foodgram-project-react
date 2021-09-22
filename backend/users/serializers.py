from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        author = obj
        return Subscribe.objects.filter(
            user=cur_user,
            author=author
        ).exists()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id',
            'username',
            'email',
            'last_name',
            'first_name',
            'is_subscribed'
        )


class UserWithRecipesSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        cur_user = self.context['request'].user
        if cur_user.is_anonymous:
            return False
        author = obj
        return Subscribe.objects.filter(
            user=cur_user,
            author=author
        ).exists()

    def get_recipes(self, obj):
        from api.serializers import PreviewRecipeSerializer
        limit = 3
        try:
            limit = self.context['request'].query_params['recipes_limit']
        except Exception:
            pass

        qs = obj.recipes.all()[:int(limit)]
        serializer = PreviewRecipeSerializer(
            instance=qs,
            many=True,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def get_recipes_count(self, obj):
        qs = obj.recipes.all()
        return qs.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Данный автор уже находиться в избранном.'
            )
        ]

    def validate(self, data):
        user = self.context['request'].user
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'На данном сервисе нет возможности '
                'подписаться на самого себя. '
                'Приносим свои извинения.'
            )
        return data

    def to_representation(self, instance):
        authors = UserWithRecipesSerializer(
            instance.author,
            context={
                'request': self.context.get('request')
            }
        )
        return authors.data
