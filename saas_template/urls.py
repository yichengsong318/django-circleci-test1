"""saas_template URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_nested import routers

from core.views import (
    RegistrationView,
    LoginView,
    ChangePasswordView,
    UserViewSet,
    NotificationSettingsView,
    StoreView,
    TimezoneView,
    SupportedCurrencyView,
    UploadedImageViewSet,
    UploadedVideoViewSet
)
from products.views import (
    ProductViewSet,
    ProductCategoryViewSet,
    ContentItemViewSet
)
from discounts.views import DiscountCodeViewSet
from emailmarketing.views import (
    EmailMarketingSettingsView
)
from customers.views import CustomerViewSet
from messaging.views import (
    MessagingSettingsView,
    ChatViewSet
)
from payments.views import StripeConnectView
from billing.views import (
    StripeCustomerView,
    StripeSubscriptionView,
    StripeBillingPortalView
)
from sites.views import (
    PageViewSet,
    BuilderPreviewAPIView,
    AddSectionToDraftSchemaAPIView,
    UpdateSectionInDraftSchemaAPIView,
    DeleteSectionFromDraftSchemaAPIView,
    MoveSectionInDraftSchemaAPIView,
    PublishChangesAPIView
)

from themes.views import (
    SiteThemeViewSet,
    SiteThemeVariableViewSet,
    SiteThemeTemplateViewSet,
    SiteThemeSectionViewSet,
    SiteThemeAssetViewSet
)


user_router = routers.DefaultRouter()
user_router.register(r'users', UserViewSet, basename='users')

image_router = routers.DefaultRouter()
image_router.register(r'images', UploadedImageViewSet, basename='images')

video_router = routers.DefaultRouter()
video_router.register(r'videos', UploadedVideoViewSet, basename='videos')

product_category_router = routers.DefaultRouter()
product_category_router.register(r'product_categories', ProductCategoryViewSet,
                                 basename='product_categories')

product_router = routers.DefaultRouter()
product_router.register(r'products', ProductViewSet, basename='products')
content_item_router = routers.NestedDefaultRouter(
    product_router, r'products', lookup='product')
content_item_router.register(
    r'content_items', ContentItemViewSet, basename='content_items')

discount_router = routers.DefaultRouter()
discount_router.register(r'discount_codes', DiscountCodeViewSet, basename='discount_codes')

customer_router = routers.DefaultRouter()
customer_router.register(r'customers', CustomerViewSet, basename='customers')

chat_router = routers.DefaultRouter()
chat_router.register(r'chats', ChatViewSet, basename="chats")

pages_router = routers.DefaultRouter()
pages_router.register(r'pages', PageViewSet, basename="pages")


theme_router = routers.DefaultRouter()
theme_router.register(r'themes', SiteThemeViewSet, basename="themes")
theme_variable_router = routers.NestedDefaultRouter(
    theme_router, r'themes', lookup="sitetheme")
theme_variable_router.register(r'variables', SiteThemeVariableViewSet,
                               basename="variables")
theme_template_router = routers.NestedDefaultRouter(
    theme_router, r'themes', lookup="sitetheme")
theme_template_router.register(r'templates', SiteThemeTemplateViewSet,
                               basename="templates")

theme_section_router = routers.NestedDefaultRouter(
    theme_router, r'themes', lookup="sitetheme")
theme_section_router.register(r'sections', SiteThemeSectionViewSet,
                              basename="sections")

theme_asset_router = routers.NestedDefaultRouter(
    theme_router, r'themes', lookup='sitetheme')
theme_asset_router.register(r'assets', SiteThemeAssetViewSet,
                            basename="assets")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('payments/', include('payments.urls')),
    path('api/v1/register/', RegistrationView.as_view(), name='register'),
    path('api/v1/log_in/', LoginView.as_view(), name='log_in'),
    path('api/v1/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/v1/refresh_token/', TokenRefreshView.as_view(),
         name='refresh_token'),

    path('api/v1/timezones/', TimezoneView.as_view(), name="timezones"),
    path('api/v1/currencies/', SupportedCurrencyView.as_view(), name="currencies"),
    path('api/v1/store/', StoreView.as_view(), name="store"),
    path('api/v1/notifications/settings/', NotificationSettingsView.as_view(),
         name="notification_settings"),
    path('api/v1/email/settings/', EmailMarketingSettingsView.as_view(),
         name="email_settings"),
    path('api/v1/messaging/settings/', MessagingSettingsView.as_view(),
         name="messaging_settings"),

    path('api/v1/payments/stripe_connect/', StripeConnectView.as_view(),
         name="stripe_connect"),
    path('api/v1/billing/stripe_customer/', StripeCustomerView.as_view(),
         name="stripe_customer"),
    path('api/v1/billing/stripe_subscribe/', StripeSubscriptionView.as_view(),
         name="stripe_subscribe"),
    path('api/v1/billing/stripe_billing_portal/',
         StripeBillingPortalView.as_view(), name="stripe_billing_portal"),

    path('api/v1/site/render_preview/', BuilderPreviewAPIView.as_view(),
         name="builder_preview"),
    path('api/v1/site/add_section_to_draft_schema/',
         AddSectionToDraftSchemaAPIView.as_view(),
         name="add_section_to_draft_schema"),
    path('api/v1/site/update_section_in_draft_schema/',
         UpdateSectionInDraftSchemaAPIView.as_view(),
         name="update_section_in_draft_schema"),
    path('api/v1/site/delete_section_from_draft_schema/',
         DeleteSectionFromDraftSchemaAPIView.as_view(),
         name="delete_section_from_draft_schema"),
    path('api/v1/site/move_section_in_draft_schema/',
         MoveSectionInDraftSchemaAPIView.as_view(),
         name="move_section_in_draft_schema"),
    path('api/v1/site/publish_changes/', PublishChangesAPIView.as_view(),
         name="publish_changes"),

    path('api/v1/', include(theme_router.urls)),
    path('api/v1/', include(theme_template_router.urls)),
    path('api/v1/', include(theme_section_router.urls)),
    path('api/v1/', include(theme_asset_router.urls)),
    path('api/v1/', include(pages_router.urls)),
    path('api/v1/', include(chat_router.urls)),
    path('api/v1/', include(customer_router.urls)),
    path('api/v1/', include(product_router.urls)),
    path('api/v1/', include(product_category_router.urls)),
    path('api/v1/', include(content_item_router.urls)),
    path('api/v1/', include(discount_router.urls)),
    path('api/v1/', include(user_router.urls)),
    path('api/v1/', include(image_router.urls)),
    path('api/v1/', include(video_router.urls))
]
