from django.shortcuts import (
    render,
    get_object_or_404
)
from django.contrib.auth.decorators import login_required
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt import tokens

from core.models import (
    Store
)

from products.models import (
    Product
)

from customers.models import (
    Customer,
    Sale
)

from customers.serializers import CustomerSerializer
from customers.utils import (
    get_customer_activity,
    get_products_and_memberships
)


class CustomerViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = CustomerSerializer
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        try:
            return Customer.objects.filter(store=self.request.user.store)
        except Customer.DoesNotExist:
            return Customer.objects.none()

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.GET.get("query")

        if query is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        results = Customer.objects.filter(email__icontains=query)
        return Response(CustomerSerializer(results, many=True).data)

    @action(detail=True, methods=['get'])
    def products_and_memberships(self, request, uuid):
        """

        :param request:
        :param customer_uuid:
        :return:
        """
        customer = get_object_or_404(Customer, uuid=uuid)
        return Response(get_products_and_memberships(customer))

    @action(detail=True, methods=['get'])
    def activity(self, request, uuid):
        """

        :param request:
        :param customer_uuid:
        :return:
        """
        customer = get_object_or_404(Customer, uuid=uuid)
        return Response(get_customer_activity(customer))


@login_required
def dashboard_home(request):
    """

    :param request:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    refresh = tokens.RefreshToken.for_user(request.user)
    customer = request.user.customer

    your_products = Product.objects.filter(
        uuid__in=[s.product.uuid for s
                  in Sale.objects.filter(customer=customer)])
    other_products = Product.objects.filter(
        store=store, draft=False).exclude(
        id__in=[p.id for p in your_products])

    return render(request, "customers/dashboard_home.html", {
        "store": store,
        "token": refresh.access_token,
        'your_products': your_products,
        "other_products": other_products
    })
