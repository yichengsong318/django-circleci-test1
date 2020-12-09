from django.shortcuts import (
    render,
    get_object_or_404
)
from rest_framework import (
    permissions,
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Store


from discounts.models import (
    DiscountCode,
    DiscountCodeUsage
)
from discounts.serializers import (
    DiscountCodeSerializer,
    DiscountCodeUsageSerializer
)


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    def get_queryset(self):
        try:
            return DiscountCode.objects.filter(store=self.request.user.store)
        except Store.DoesNotExist:
            return DiscountCode.objects.none()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """

        :param request:
        :return:
        """
        query = request.GET.get("query")

        if query is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        results = DiscountCode.objects.filter(code__icontains=query)
        return Response(DiscountCodeSerializer(results, many=True).data)

    @action(detail=True, methods=['get'])
    def usages(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        code = get_object_or_404(
            DiscountCode, store=request.user.store, uuid=uuid)
        usages = DiscountCodeUsage.objects.filter(discount_code=code)
        return Response(DiscountCodeUsageSerializer(usages, many=True).data)
