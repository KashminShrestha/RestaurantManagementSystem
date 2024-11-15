"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BillViewSet,
    CategoryViewSet,
    MenuItemViewSet,
    MenuViewSet,
    OrderViewSet,
    ReceptionViewSet,
    ReservationViewSet,
    TableViewSet,
    WaiterViewSet,
)

router = DefaultRouter()
router.register(r"Tables", TableViewSet)
router.register(r"Categories", CategoryViewSet)
router.register(r"Menus", MenuViewSet)
router.register(r"MenuItems", MenuItemViewSet)
router.register(r"Waiters", WaiterViewSet)
router.register(r"Receptions", ReceptionViewSet)
router.register(r"Orders", OrderViewSet)
router.register(r"Bills", BillViewSet)
router.register(r"Reservations", ReservationViewSet)

# urlpatterns = [
#     path("", include(router.urls)),
# ]
urlpatterns = [] + router.urls
