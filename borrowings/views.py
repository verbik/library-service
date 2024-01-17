from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from borrowings.filters import BorrowingsFilter
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
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

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

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
