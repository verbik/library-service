from datetime import date, timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(
        validators=[MinValueValidator(limit_value=date.today)],
        default=date.today() + timedelta(weeks=2),
    )
    actual_return_date = models.DateField(
        null=True, blank=True, validators=[MinValueValidator(limit_value=date.today)]
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["expected_return_date"]

    def message(self) -> str:
        return (
            f"Borrowing {self.id}\n"
            f"Borrowed on {self.borrow_date}\n"
            f"Expected to be returned on {self.expected_return_date}.\n\n"
            f"Book borrowed: {self.book}.\n"
            f"{self.book.inventory} left in inventory.\n\n"
            f"User email: {self.user}\n"
            f"Id: {self.user_id}"
        )

    def __str__(self):
        return f"{self.book.title}, expected return date: {self.expected_return_date}."
