from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from main.models import Order
from main.utils import logger


@login_required
@require_POST
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.cancel()
        logger.info(f"Пользователь {request.user.username} отменил заказ #{order_id}")
        return JsonResponse({"status": "ok"})
    except Order.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Заказ не найден"}, status=404)