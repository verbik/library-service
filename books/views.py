from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer
from books.models import Book


class BookPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination
    permission_classes = (IsAdminOrReadOnly,)
