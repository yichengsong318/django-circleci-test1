import io
import uuid
import stripe
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
    redirect
)
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
from django.db import transaction
from core.models import (
    Store,
    User,
    SupportedCurrency,
    PasswordResetKey,
    UploadedImage
)
from core.utils import (
    send_password_reset_email
)
from core.decorators import (
    anonymous_required,
    customer_has_access
)
from stores.forms import (
    RegistrationForm,
    PasswordResetForm,
    SetPasswordForm,
    GetAccessForm,
    EmailSubscriberForm
)
from customers.models import (
    Customer,
    Sale
)

from products.models import (
    Product
)

from payments.models import StripeConnect
from discounts.models import (
    DiscountCode,
    DiscountCodeUsage
)


from saas_template.settings import (
    STRIPE_SECRET_KEY,
    STRIPE_PUBLISHABLE_KEY
)

from customers.utils import get_owned_product_redirect
from stores.utils import calculate_sale_amount
from emailmarketing.models import EmailSubscriber

from themes.models import (
    SiteTheme,
    SiteThemeAsset,
    SiteThemeTemplate
)

import mimetypes
from sites.renderutils import (
    render as render_theme_template
)

stripe.api_key = STRIPE_SECRET_KEY


def store_custom_css(request):
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    return render(
        request, "stores/css/custom.css",
        {"store": store},
        content_type="text/css"
    )


def store_theme_asset(request, theme_uuid, asset_name):
    """

    :param request:
    :param theme_uuid:
    :param asset_name:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    theme = get_object_or_404(SiteTheme, store=store, uuid=theme_uuid)
    asset = get_object_or_404(
        SiteThemeAsset, site_theme=theme, name=asset_name)

    content_type, encoding = mimetypes.guess_type(asset.name)
    print(content_type)
    content_type = content_type or 'application/octet-stream'
    response = HttpResponse(bytes(asset.content),
                            content_type=content_type)
    response['Content-Length'] = len(asset.content)
    return response


def store_uploaded_image(request, image_uuid):
    """

    :param request:
    :param image_uuid:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    image = get_object_or_404(UploadedImage, store=store, uuid=image_uuid)
    content_type, encoding = mimetypes.guess_type(image.name)

    content_type = content_type or 'application/octet-stream'
    response = HttpResponse(bytes(image.content),
                            content_type=content_type)
    response['Content-Length'] = len(image.content)
    return response



def store_home(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    active_theme = get_object_or_404(SiteTheme,
                                     store=store, live=True)
    template = get_object_or_404(
        SiteThemeTemplate,
        site_theme=active_theme,
        template_type="INDEX")

    src = render_theme_template(template, context={
        "user": request.user,
        "store": store,
        "theme": active_theme,
        "sections": store.schema
    })

    return HttpResponse(src)


@csrf_protect
@anonymous_required
def store_login(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    if request.user.is_authenticated:
        return redirect("customer_dashboard_home")

    params = {
        "store": store,
        "errors": []
    }

    if request.method == "POST":
        user = authenticate(email=request.POST.get("email"),
                            password=request.POST.get("password"),
                            store=store)

        if user is not None and user.is_active:
            login(request, user)
            return redirect("customer_dashboard_home")

        params["errors"].append("Incorrect username and password.")

    return render(request, "stores/login.html", params)


@login_required
def store_logout(request):
    """

    :param request:
    :return:
    """
    logout(request)
    return redirect("store_home")


@anonymous_required
def store_register(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    if request.user.is_authenticated:
        return redirect("customer_dashboard_home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        form.add_store(store)

        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=str(uuid.uuid4()),
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    customer_of=store
                )

                try:
                    customer = Customer.objects.get(
                        store=store, email=user.email)
                    customer.user = user
                    customer.save()

                except Customer.DoesNotExist:
                    Customer.objects.create(
                        store=store, email=user.email, user=user)

            return redirect("store_registration_complete")

    else:
        form = RegistrationForm()

    return render(request, "stores/register.html", {
        "store": store,
        "form": form
    })


def store_registration_complete(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    return render(request, "stores/registration_complete.html", {
        "store": store
    })


@anonymous_required
def store_reset_password(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        form.add_store(store)

        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data["email"],
                                    customer_of=store)
            send_password_reset_email(user, store)

            return render(request, "stores/reset_password_sent.html", {
                "store": store,
                "email": user.email
            })
    else:
        form = PasswordResetForm()

    return render(request, "stores/reset_password.html", {
        "store": store,
        "form": form
    })


@anonymous_required
def store_reset_password_confirm(request, key):
    """

    :param request:
    :param key:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    key = get_object_or_404(
        PasswordResetKey, store=store, key=key, used=False, expires__gte=timezone.now())
    user = key.user

    if request.method == "POST":
        form = SetPasswordForm(request.POST)

        if form.is_valid():
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            key.used = True
            key.save()

            return redirect("store_reset_password_done")
    else:
        form = SetPasswordForm()

    return render(request, "stores/reset_password_confirm.html", {
        "store": store,
        "key": key,
        "form": form
    })


@anonymous_required
def store_reset_password_done(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])

    return render(request, "stores/reset_password_done.html", {
        "store": store
    })


def store_product(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)

    return render(request, "stores/product.html", {
        "store": store,
        "product": product
    })


def store_buy_product(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)

    if product.free:
        return redirect("store_get_access", product_slug)

    currency = get_object_or_404(SupportedCurrency, code=store.currency)

    # Redirect if user owns product already
    if not request.user.is_anonymous:
        if Sale.objects.filter(
                customer=request.user.customer,
                product=product).exists():
            return get_owned_product_redirect(product)

    stripe_connect = get_object_or_404(StripeConnect, store=store)

    get_payment_intent_url = reverse("store_get_payment_intent",
                                     args=[product.slug])
    buy_success_redirect_url = reverse(
        "store_buy_product_success", args=[product.slug])

    return render(request, "stores/buy_product.html", {
        "store": store,
        "customer": request.user.customer if hasattr(request.user, "customer") else None,
        "product": product,
        "formatted_price": currency.format_string.format(product.price),
        "STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY,
        "connected_account_id": stripe_connect.connected_account_id,
        "get_payment_intent_url": get_payment_intent_url,
        "buy_success_redirect_url": buy_success_redirect_url
    })


@csrf_exempt
def store_get_payment_intent(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    DISCOUNT_CODE_INVALID_MSG = "Your discount code is invalid."

    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)

    if request.method == "POST":
        discount_code_string = request.POST.get("discount_code")

        if discount_code_string:
            try:
                discount_code = DiscountCode.objects.get(store=store,
                                             code=discount_code_string,
                                             active=True)

                if any([
                    discount_code.max_usages <= discount_code.num_usages,
                    discount_code.expiry and discount_code.expiry <= timezone.now()
                ]):
                    return JsonResponse(
                        {"message": DISCOUNT_CODE_INVALID_MSG}, status=400)

            except DiscountCode.DoesNotExist:
                return JsonResponse(
                    {"message": DISCOUNT_CODE_INVALID_MSG}, status=400)

        else:
            discount_code = None

        currency = get_object_or_404(SupportedCurrency, code=store.currency)
        stripe_connect = get_object_or_404(StripeConnect, store=store)
        amount = calculate_sale_amount(product, discount_code, currency)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency.code,
            stripe_account=stripe_connect.connected_account_id,
            metadata={
                "store": str(store.uuid),
                "product": str(product.uuid),
                "discount": str(discount_code.uuid) if discount_code else None,
                "user": str(request.user.uuid) if hasattr(request.user,
                                                          "uuid") else None
            }
        )

        return JsonResponse({
            "payment_intent_client_secret": payment_intent.client_secret,
            "amount": amount / currency.multiple,
            "formatted_price": currency.format_string.format(amount/currency.multiple)
        })

    return HttpResponseBadRequest()


def store_buy_product_success(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)

    customer_email = request.GET.get("customer_email")

    return render(request, "stores/buy_product_success.html", {
        "store": store,
        "product": product,
        "customer_email": customer_email
    })


def store_get_access(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)

    if not product.free:
        return redirect("store_buy_product", product_slug)

    if request.method == "POST":
        form = GetAccessForm(request.POST)
        if form.is_valid():
            try:
                customer = Customer.objects.get(
                    store=store, email=form.cleaned_data["email"])

                if form.cleaned_data["marketing"]:
                    customer.accepts_marketing = True
                    customer.save()

            except Customer.DoesNotExist:
                customer = Customer.objects.create(
                    store=store, email=form.cleaned_data["email"],
                    first_name=form.cleaned_data["first_name"],
                    accepts_marketing=form.cleaned_data["marketing"])


            Sale.objects.create(
                store=store, customer=customer, product=product, was_free=True)

            return redirect("store_get_access_success",
                     product_slug, str(customer.uuid))

    else:
        form = GetAccessForm()

    return render(request, "stores/get_access.html", {
        "store": store,
        "product": product,
        "form": form
    })


def store_get_access_success(request, product_slug, customer_uuid):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(Product, store=store, slug=product_slug)
    customer = get_object_or_404(Customer, store=store, uuid=customer_uuid)

    if request.method == "POST":
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Create user, log them in, and redirect them to the product page.

            user = User.objects.create_user(
                username=str(uuid.uuid4()),
                first_name=customer.first_name,
                email=customer.email,
                password=form.cleaned_data["new_password"],
                customer_of=store
            )

            customer.user = user
            customer.save()

            login(request, user)

    else:
        form = SetPasswordForm()

    return render(request, "stores/get_access_success.html", {
        "store": store,
        "product": product,
        "customer": customer,
        "form": form
    })


@customer_has_access
@login_required
def store_pre_launch(request, product_slug):
    """
    When a customer has bought a product and it has not been released
    yet, this is the page that shows.

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    product = get_object_or_404(
        Product, store=store, slug=product_slug, draft=False)

    return render(request, "stores/pre_launch.html", {
        "store": store,
        "product": product
    })


@csrf_exempt
@require_http_methods(['POST'])
def store_email_subscribe(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    form = EmailSubscriberForm(request.POST)

    if form.is_valid():
        try:
            existing = EmailSubscriber.objects.get(
                store=store,
                email=form.cleaned_data["email"])

        except EmailSubscriber.DoesNotExist:
            subscriber = EmailSubscriber.objects.create(
                store=store,
                first_name=form.cleaned_data["first_name"],
                email=form.cleaned_data["email"]
            )

        return JsonResponse(data={"result": "subscribed"}, status=200)
    else:
        return JsonResponse(data={"result": "error",
                                  "errors": form.errors}, status=400)
