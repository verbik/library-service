import os
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingDetailSerializer

BORROWING_URL = reverse("borrowings-list")


def sample_borrowing(book: Book, user: settings.AUTH_USER_MODEL):
    return Borrowing.objects.create(book=book, user=user)


def sample_book(**params):
    defaults = {
        "title": "Test Title",
        "author": "Test Author",
        "cover": "HARD",
        "inventory": 2,
        "daily_fee": Decimal("0.5"),
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(borrowing_id):
    return reverse("borrowings-detail", args=[borrowing_id])


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testuser@email.com", "testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.book = sample_book()

    def test_list_borrowings(self):
        another_user = get_user_model().objects.create_user(
            "test2@test.com", "testpass"
        )

        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=another_user, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user, book=self.book)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        borrowings_payload = {"book": self.book.id, "user": self.user.id}
        res = self.client.post(BORROWING_URL, borrowings_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=res.data["id"])
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        book_updated = Book.objects.get(id=self.book.id)
        self.assertEqual(book_updated.inventory, self.book.inventory - 1)

    def test_cannot_create_when_book_inventory_zero(self):
        book = sample_book(inventory=0)
        res = self.client.post(BORROWING_URL, {"book": self.book})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self):
        borrowing_payload = {"book": self.book.id, "user": self.user}
        create_res = self.client.post(BORROWING_URL, borrowing_payload)
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        url = reverse("borrowings-return-borrowing", args=[self.book.id])
        res = self.client.post(url)

        borrowing = Borrowing.objects.get(id=self.book.id)
        self.assertEqual(borrowing.actual_return_date, datetime.today().date())

        self.assertEqual(borrowing.book.inventory, self.book.inventory)


class AdminBorrowingsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "testsuperuser@email.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_list_borrowings(self):
        second_user = get_user_model().objects.create_user(
            "testseconduser@email.com", "testpassword"
        )

        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_delete_not_allowed(self):
        borrowing = sample_borrowing(user=self.user, book=self.book)
        url = detail_url(borrowing.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filter_borrowing_by_active(self):
        second_user = get_user_model().objects.create_user(
            "testuser2@email.com", "testpassword"
        )

        borrowing = sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=second_user, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        return_url = reverse("borrowings-return-borrowing", args=[borrowing.id])
        self.client.post(return_url)

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        borrowings = Borrowing.objects.filter(actual_return_date=None)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.data, serializer.data)
