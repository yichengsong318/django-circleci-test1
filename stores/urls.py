from django.urls import path, re_path
from stores.views import (
    store_home,

    store_login,
    store_logout,

    store_register,
    store_registration_complete,

    store_reset_password,
    store_reset_password_confirm,
    store_reset_password_done,

    store_product,
    store_buy_product,
    store_buy_product_success,
    store_get_payment_intent,
    store_pre_launch,

    store_get_access,
    store_get_access_success,

    store_custom_css,
    store_theme_asset,
    store_uploaded_image,

    store_email_subscribe
)

urlpatterns = [
    path('', store_home, name='store_home'),
    path('login/', store_login, name="store_login"),
    path('logout/', store_logout, name="store_logout"),

    path('register/', store_register, name="store_register"),
    path('registration_complete/', store_registration_complete,
         name="store_registration_complete"),

    path('reset_password/', store_reset_password, name="store_reset_password"),
    re_path(r"^reset_password/(?P<key>[a-z0-9]{64})/$",
         store_reset_password_confirm, name="store_reset_password_confirm"),
    path('reset_password/done/', store_reset_password_done,
         name="store_reset_password_done"),


    path('products/<slug:product_slug>/', store_product, name="store_product"),
    path('products/<slug:product_slug>/buy/', store_buy_product,
         name="store_buy_product"),
    path('products/<slug:product_slug>/get_payment_intent/',
         store_get_payment_intent, name="store_get_payment_intent"),
    path('products/<slug:product_slug>/buy/success/',
         store_buy_product_success, name="store_buy_product_success"),

    path('products/<slug:product_slug>/get_access/', store_get_access,
         name="store_get_access"),
    path('products/<slug:product_slug>/get_access_success/<uuid:customer_uuid>/',
         store_get_access_success, name="store_get_access_success"),

    path('prelaunch/<slug:product_slug>/', store_pre_launch,
         name="store_pre_launch"),

    path('custom.css', store_custom_css, name="store_custom_css"),
    path('themes/<uuid:theme_uuid>/assets/<str:asset_name>',
         store_theme_asset, name="store_theme_asset"),
    path('images/<uuid:image_uuid>/', store_uploaded_image,
         name="store_uploaded_image"),

    path('email_subscribe/', store_email_subscribe,
         name="store_email_subscribe")
]
