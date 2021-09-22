from django.shortcuts import HttpResponse, get_object_or_404
from django_filters import rest_framework as django_filters
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientFilter, RecipeFilter
from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (AddRecipeSerializer, CartSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class LimitFieldPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class TagViewSet(viewsets.ModelViewSet):
    """API тэгов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """API ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """API рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (AdminOrAuthorOrReadOnly,)
    pagination_class = LimitFieldPagination
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return AddRecipeSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class FavoriteView(APIView):
    """API избранных рецептов."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        cur_user = request.user
        req_fav_data = {
            'owner': cur_user.id,
            'recipe': recipe_id
        }
        fav_context = {'request': request}
        serializer = FavoriteSerializer(
            data=req_fav_data,
            context=fav_context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, recipe_id):
        cur_user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Favorite.objects.filter(
                owner=cur_user,
                recipe=recipe
        ).exists():
            return Response(
                'Этот рецепт отсутсвует в избранном.',
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.filter(
            owner=cur_user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    """API списка покупок рецептов."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        cur_user = self.request.user
        req_cart_data = {
            'owner': cur_user.id,
            'recipe': recipe_id
        }
        cart_context = {'request': request}
        serializer = CartSerializer(data=req_cart_data, context=cart_context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        cur_user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Cart.objects.filter(
                owner=cur_user,
                recipe=recipe
        ).exists():
            return Response('Рецепта нет в списке покупок.', status=status.HTTP_400_BAD_REQUEST)
        Cart.objects.filter(
            owner=cur_user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadCart(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        cur_user = request.user
        shop_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__shop_recipes__owner=cur_user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shop_list:
                shop_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit
                }
            else:
                shop_list[name][amount] += amount
        out_list = ['Foodgram\n\n']
        for ingr, value in shop_list.items():
            out_list.append(
                f" {ingr} - {value['amount']} "
                f"{value['measurement_unit']}\n"
            )
        # print(out_list)
        response = HttpResponse(out_list, {
            'Content-Type': 'text/plain',
            'Content-Disposition': 'attachment; filename="out_list.txt"',
        })
        return response
