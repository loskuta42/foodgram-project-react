from api.views import LimitFieldPagination

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscribe
from .serializers import SubscriptionSerializer, UserWithRecipesSerializer

User = get_user_model()


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        cur_user = request.user
        sub_data = {
            'user': cur_user.id,
            'author': user_id
        }
        sub_context = {'request': request}
        serializer = SubscriptionSerializer(
            data=sub_data,
            context=sub_context
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

    def delete(self, request, user_id):
        cur_user = request.user
        author = get_object_or_404(User, id=user_id)
        if not Subscribe.objects.filter(
                user=cur_user,
                author=author
        ).exists():
            return Response(
                'Автора нет в подписках.',
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.filter(
            user=cur_user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitFieldPagination
    serializer_class = UserWithRecipesSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        cur_user = self.request.user
        return User.objects.filter(
            subscribing__user=cur_user
        )
