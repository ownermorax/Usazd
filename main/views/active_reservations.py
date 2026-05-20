from main.models import Profile, Order
from django.shortcuts import redirect, render
from main.utils import logger


def active_reservations(request):
    """Отображение активных бронирований пользователя"""
    logger.info("Пользователь зашел на страницу с активными бронированиями.")
    if not request.user.is_authenticated:
        return redirect("auth")

    orders = list(
        Order.objects.filter(user=request.user, status="active").prefetch_related(
            "reservations__train", "reservations__station_in", "reservations__station_out"
        )
    )

    total_places = sum(order.reservations.count() for order in orders)

    logger.debug(
        f"Найдено заказов: {len(orders)} для пользователя #{request.user.id}."
    )
    logger.info(f"total_places = {total_places}")

    return render(request, "active_reservations.html", {
        "orders": orders,
        "total_places": total_places,
    })