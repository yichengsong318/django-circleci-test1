from django.urls import path, re_path
from payments.views import (
    stripe_connect_redirect,
    stripe_connect_webhook
)

urlpatterns = [
    path('stripe_connect_redirect/', stripe_connect_redirect,
         name="stripe_connect_redirect"),
    path('stripe_connect_webhook/', stripe_connect_webhook,
         name="stripe_connect_webhook")
]
