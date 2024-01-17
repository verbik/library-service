from django.urls import path, include
from rest_framework import routers

from borrowings.views import BorrowingsViewSet

router = routers.DefaultRouter()
router.register("", BorrowingsViewSet)

urlpatterns = router.urls

app_name = "borrowings"