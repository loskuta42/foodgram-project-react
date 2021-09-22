from django.urls import path, re_path

from .views import SubscribeView, SubscriptionsView

urlpatterns = [
    re_path(
        r'(?P<user_id>[0-9]+)/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions'
    )
]
