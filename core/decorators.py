from django.shortcuts import redirect
from saas_template.settings import LOGIN_REDIRECT_URL
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.http import Http404

from products.models import Product
from customers.models import Sale


def anonymous_required(func):
    """

    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):

        redirect_to = kwargs.get('next', LOGIN_REDIRECT_URL )
        if request.user.is_authenticated:
            return redirect(redirect_to)

        response = func(request, *args, **kwargs)
        return response

    return inner


def product_is_published(fn):
    """

    :param fn:
    :return:
    """
    def inner(request, product_slug, *args, **kwargs):
        product = get_object_or_404(
            Product, store=request.user.customer_of, slug=product_slug)

        if product.published:
            return fn(request, product_slug, *args, **kwargs)
        elif product.pre_sale:
            return redirect("store_pre_launch", product_slug)
        else:
            raise Http404

    return inner


def customer_has_access(fn):
    """

    :param fn:
    :return:
    """
    def inner(request, product_slug, *args, **kwargs):
        product = get_object_or_404(
            Product, store=request.user.customer_of, slug=product_slug)

        if Sale.objects.filter(
                store=request.user.customer_of,
                customer=request.user.customer,
                product=product):
            return fn(request, product_slug, *args, **kwargs)

        return redirect("store_product", product_slug)

    return inner
