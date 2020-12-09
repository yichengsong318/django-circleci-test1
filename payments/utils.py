from urllib.parse import quote
from saas_template.settings import STRIPE_CONNECT_CLIENT_ID
from payments.models import (
    StripeConnect,
)

from core.models import (
    User,
    Store,
    SupportedCurrency
)
from customers.models import (
    Customer,
    Sale
)
from products.models import Product
from payments.models import (
    Payment
)
from discounts.models import (
    DiscountCode,
    DiscountCodeUsage
)



def get_connect_url(state, scope, user_email):
    """

    :return:
    """
    return "https://connect.stripe.com/oauth/authorize?client_id={0}&state={1}&scope={2}&response_type=code&stripe_user[email]={3}".format(
        STRIPE_CONNECT_CLIENT_ID,
        quote(state),
        scope,
        quote(user_email)
    )


def deauthorize_account(connected_account_id):
    """

    :param connected_account_id:
    :return:
    """
    StripeConnect.objects.filter(
        connected_account_id=connected_account_id).update(
        connected_account_id=None)


def payment_succeeded(event):
    """

    :param payload:
    :return:
    """
    StripeConnect.objects.get(connected_account_id=event["account"])

    payment_intent_id = event["data"]["object"]["id"]
    charge_data = event["data"]["object"]["charges"]["data"][0]
    metadata = charge_data["metadata"]
    billing_details = charge_data["billing_details"]

    print(metadata)

    store = Store.objects.get(uuid=metadata["store"])
    product = Product.objects.get(uuid=metadata["product"])
    currency = SupportedCurrency.objects.get(
        code=charge_data["currency"].upper())

    if "user" in metadata:
        user = User.objects.get(uuid=metadata["user"], customer_of=store)
    else:
        user = None

    if user:
        customer = user.customer
    else:
        try:
            customer = Customer.objects.get(
                store=store, email=billing_details["email"])
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                store=store, email=billing_details["email"])

    # TODO: different process for payments of subscription invoices

    try:
        sale = Sale.objects.get(store=store, customer=customer, product=product)
    except Sale.DoesNotExist:
        sale = Sale.objects.create(
            store=store, customer=customer, product=product)

    try:
        Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
    except Payment.DoesNotExist:
        Payment.objects.create(
            store=store,
            sale=sale,
            stripe_payment_intent_id=payment_intent_id,
            amount=charge_data["amount"] / currency.multiple,
            currency=currency.code
        )

    if "discount" in metadata:
        try:
            discount_code = DiscountCode.objects.get(
                store=store, uuid=metadata["discount"])

            if not DiscountCodeUsage.objects.filter(
                    store=store, discount_code=discount_code, sale=sale).exists():

                DiscountCodeUsage.objects.create(
                    store=store, discount_code=discount_code, sale=sale)
        except DiscountCode.DoesNotExist:
            pass
