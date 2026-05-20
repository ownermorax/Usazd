"""
URL configuration for USAZD project.

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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from main import views
from main.views.cancel_reservation import cancel_reservation

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.main, name="main"),
    path("info/", views.info, name="info"),
    path("user-info/", views.user_info, name="user_info"),
    path("user-info/edit", views.edit_user_info, name="edit_user_info"),
    path("active-reservations/", views.active_reservations, name="active_reservations"),
    path("reservation-history/", views.reservation_history, name="reservation_history"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("reg/", views.reg, name="reg"),
    path("timetable/", views.timetable, name="timetable"),
    path("api/search/", views.timetable_handler, name="timetable_api"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth/", LoginView.as_view(), name="auth"),
    path("train/", views.train, name="train"),
    path("balance/", views.update_balance, name="balance"),
    path("api/create/reservation/", views.reservation_handler, name="create_reservation"),
    path(
        "api/cancel/<int:reservation_id>/",
        cancel_reservation,
        name="cancel_reservation",
    ),
    path("<str:username>/vip/", views.vip, name="vip"),
    path("api/vip/pay", views.vip_handler, name="vip_api"),
    path(
        "schedule/<str:from_station>/<str:to_station>/",
        views.schedule_card,
        name="schedule_card",
    ),
    path("quick-booking/", views.quick_booking, name="quick_booking"),
    path("api/cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
