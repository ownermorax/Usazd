from django.http import JsonResponse
from main.api_instance import yandex_api
from main.utils import logger

def get_stations(request):
    """API endpoint для получения списка станций"""
    try:
        stations = list(yandex_api.stations_id.keys())
        
        logger.info(f"Отправлен список станций: {len(stations)} шт.")
        
        return JsonResponse({
            'status': 'ok',
            'stations': stations,
            'total': len(stations)
        })
        
    except Exception as e:
        logger.error(f"Ошибка при получении станций: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)