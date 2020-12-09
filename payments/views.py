import uuid
import json
import stripe
import stripe.error
import stripe.oauth_error
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse,
    redirect
)
from django.http import (
    HttpResponse,
    HttpResponseBadRequest
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash
)
from core.models import (
    Store,
    User
)

from payments.serializers import StripeConnectSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions
)

from payments.models import StripeConnect
from payments.utils import (
    deauthorize_account,
    payment_succeeded
)


from saas_template.settings import (
    STRIPE_SECRET_KEY,
    STRIPE_CONNECT_WEBHOOK_SECRET,
    STRIPE_CONNECT_REDIRECT_URL
)


stripe.api_key = STRIPE_SECRET_KEY

class StripeConnectView(APIView):
    """

    """
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:
        """
        try:
            stripe_connect = StripeConnect.objects.get(
                store=request.user.store)
        except StripeConnect.DoesNotExist:
            stripe_connect = StripeConnect.objects.create(
                store=request.user.store)

        return Response(StripeConnectSerializer(stripe_connect).data)


def stripe_connect_redirect(request):
    """

    :param request:
    :return:
    """
    if "state" not in request.GET or "code" not in request.GET:
        return HttpResponseBadRequest()

    redirect_state = request.GET.get("state")
    stripe_connect = get_object_or_404(StripeConnect,
                                       redirect_state=redirect_state)

    code = request.GET.get("code")

    try:
        response = stripe.OAuth.token(
            grant_type="authorization_code", code=code)

    except stripe.oauth_error.OAuthError as ex:
        return HttpResponseBadRequest()
    except Exception as ex:
        raise ex

    stripe_connect.connected_account_id = response["stripe_user_id"]
    stripe_connect.save()

    return redirect(STRIPE_CONNECT_REDIRECT_URL)


@csrf_exempt
def stripe_connect_webhook(request):
    """

    :param request:
    :return:
    """
    if "HTTP_STRIPE_SIGNATURE" not in request.META:
        return HttpResponseBadRequest()

    signature = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload=request.body,
            sig_header=signature,
            secret=STRIPE_CONNECT_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload.
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError as e:
        # Invalid Signature.
        return HttpResponseBadRequest()

    if event["type"] == "account.application.deauthorized":
        deauthorize_account(event["account"])

        print(event)
    elif event["type"] == "account.updated":
        print(event)
    elif event["type"] == "account.external_account.updated":
        print(event)
    elif event["type"] == "payment_intent.succeeded":
        payment_succeeded(event)
        print(event)


    return HttpResponse(status=200)