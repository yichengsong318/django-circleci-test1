import stripe
from django.shortcuts import (
    render,
    get_object_or_404
)
from rest_framework import (
    permissions,
    status
)
from rest_framework.views import APIView
from rest_framework.response import Response

from billing.models import (
    StripeCustomer,
    StripeSubscription
)
from billing.serializers import (
    StripeCustomerSerializer,
    StripeSubscriptionSerializer,
    StripeBillingPortalSerializer
)

from saas_template.settings import (
    STRIPE_SECRET_KEY,
    STRIPE_PRICE_IDS,
    STRIPE_PORTAL_RETURN_URL
)


stripe.api_key = STRIPE_SECRET_KEY


class StripeBillingPortalView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :return:
        """
        stripe_customer = get_object_or_404(StripeCustomer,
                                            store=request.user.store)

        bp = stripe.billing_portal.Session.create(
            customer=stripe_customer.stripe_customer_id,
            return_url=STRIPE_PORTAL_RETURN_URL
        )

        return Response(StripeBillingPortalSerializer(bp).data)


class StripeCustomerView(APIView):
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:
        """
        try:
            cust = StripeCustomer.objects.get(store=request.user.store)
        except StripeCustomer.DoesNotExist:
            cust = StripeCustomer.objects.create(store=request.user.store)

        return Response(StripeCustomerSerializer(cust).data)


class StripeSubscriptionView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        print(request.data)

        plan = request.data["plan"]
        payment_method_id = request.data["payment_method_id"]
        plan_price_id = STRIPE_PRICE_IDS[plan]

        stripe_customer = get_object_or_404(StripeCustomer,
                                            store=request.user.store)

        try:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer.stripe_customer_id)

            stripe.Customer.modify(
                stripe_customer.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )

            stripe_customer.stripe_payment_method_id = payment_method_id
            stripe_customer.save()

            subscription = stripe.Subscription.create(
                customer=stripe_customer.stripe_customer_id,
                items=[{"price": plan_price_id}],
                expand=['latest_invoice.payment_intent']
            )

            # Delete any existing subscriptions
            StripeSubscription.objects.filter(
                stripe_customer=stripe_customer).delete()

            stripe_subscription = StripeSubscription.objects.create(
                stripe_customer=stripe_customer,
                subscription_id=subscription.id,
                plan=plan,
                status=subscription.status,
                latest_invoice_payment_intent_status=subscription.latest_invoice.payment_intent.status
            )

            return Response(StripeSubscriptionSerializer(stripe_subscription).data)

        except Exception as ex:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": str(ex)})

