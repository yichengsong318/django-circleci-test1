from django.urls import path, re_path
from courses.views import (
    course_home,
    course_content_item,
    course_preview,
    content_preview
)

urlpatterns = [
    path('<slug:product_slug>/', course_home, name='course_home'),
    path('<slug:product_slug>/<uuid:content_uuid>/', course_content_item, name="course_content_item"),
    path('<slug:product_slug>/preview/', course_preview, name='course_preview'),
    path('<slug:product_slug>/<uuid:content_uuid>/preview/', content_preview, name="content_preview")
]
