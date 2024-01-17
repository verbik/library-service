import django_filters

from borrowings.models import Borrowing


class BorrowingsFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(
        field_name="actual_return_date", lookup_expr="isnull", label="Is Active"
    )

    class Meta:
        model = Borrowing
        fields = ["is_active"]
