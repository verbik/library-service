from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from books.models import Book
from books.serializers import BookSerializer


BOOKS_URL = reverse("books-list")

BOOK_PAYLOAD = {
    "title": "Test Title",
    "author": "Test Author",
    "cover": "HARD",
    "inventory": 2,
    "daily_fee": Decimal("0.5"),
}


def detail_url(book_id):
    return reverse("books-detail", args=[book_id])


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


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOKS_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        res = self.client.post(BOOKS_URL, BOOK_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTests(UnauthenticatedBooksApiTests):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_authenticated@email.com",
            "password",
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        res = self.client.post(BOOKS_URL, BOOK_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBooksApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "testuser@gmail.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        res = self.client.post(BOOKS_URL, BOOK_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in BOOK_PAYLOAD.keys():
            self.assertEqual(BOOK_PAYLOAD[key], getattr(book, key))

    def test_update_book(self):
        book = sample_book()
        payload = {
            "title": "Changed Title",
            "author": "Test Author",
            "cover": "SOFT",
            "inventory": 2,
            "daily_fee": Decimal("0.7"),
        }
        url = detail_url(book.id)
        res = self.client.put(url, payload)

        book = Book.objects.get(id=book.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()
        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        book = Book.objects.first()
        self.assertEqual(None, book)
