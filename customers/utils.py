from django.shortcuts import redirect

def get_customer_activity(customer):
    """
    Eventually, we should include all this:

    Sign up
    Account created
    verified email
    Sales
    Messages
    Log ins
    Joined membership
    Paid invoice
    other invoice events
    Cancelled membership
    completed course
    Downloaded something
    Clicked on link in email

    :param customer:
    :return:
    """

    activity = []

    activity.append({
        "type": "FIRST_SEEN",
        "message": "First seen.",
        "datetime": customer.created_at,
        "datetime_display": customer.created_at.strftime("%B %e, %Y")
    })

    if customer.user:
        activity.append({
            "type": "ACCOUNT_CREATED",
            "message": "Created an account.",
            "datetime": customer.user.date_joined,
            "datetime_display": customer.user.date_joined.strftime("%B %e, %Y")
        })

    for sale in customer.sales:
        activity.append({
            "type": "SALE",
            "message": "Bought {0}.".format(sale.product.name),
            "datetime": sale.created_at,
            "datetime_display": sale.created_at.strftime("%B %e, %Y")
        })

    return sorted(activity, key=lambda s: s["datetime"], reverse=True)


def get_products_and_memberships(customer):
    """

    :param customer:
    :return:
    """

    pm = []

    for sale in customer.sales:
        pm.append({
            "type": sale.product.product_type,
            "name": sale.product.name
        })

    return pm


def get_owned_product_redirect(product):
    """

    :param product:
    :return:
    """
    if product.product_type == "course":
        return redirect("course_home", product.slug)

    return redirect("dashboard_home")
