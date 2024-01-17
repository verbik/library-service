from datetime import date

from django.db import transaction
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowings.filters import BorrowingsFilter
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingsViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    permission_classes = [IsAuthenticated]
    filterset_class = BorrowingsFilter

    def get_queryset(self):
        queryset = Borrowing.objects.prefetch_related("book", "user")

        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        if user.is_staff:
            customer_id = self.request.query_params.get("user_id")
            if customer_id:
                queryset = queryset.filter(user__id=customer_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory > 0:
            book.inventory -= 1
            book.save()
        else:
            raise ValidationError(
                "There are no books left in inventory. Cannot borrow."
            )

        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_borrowing(self, request, pk=None):
        """Endpoint for returning borrowing."""
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {
                    "detail": "This borrowing has been already returned. You cannot return it twice."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            book = borrowing.book
            book.inventory += 1
            book.save()

            borrowing.actual_return_date = date.today()
            borrowing.save()

        return Response(status=status.HTTP_200_OK)
