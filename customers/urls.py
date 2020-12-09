from django.urls import path, re_path
from customers.views import (
    dashboard_home
)

urlpatterns = [
    path('', dashboard_home, name='customer_dashboard_home')
]
