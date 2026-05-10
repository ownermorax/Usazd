from django.http import JsonResponse
from django.contrib.auth.models import User
from djmoney.money import Money
from main.models import Train, Profile, Reservation, Station
import json


def reservation_handler(request):
    """Обработчик бронирования мест в поезде.
    Принимает GET-запрос с параметрами бронирования, проверяет наличие мест,
    списывает средства с баланса пользователя и создаёт запись о бронировании.

    :param request: HTTP GET-запрос
    :var user_id: ID пользователя
    :var train_id: ID поезда
    :var seats: Места в вагоне
    :var station_in: ID станции посадки
    :var station_in_name: Название станции посадки
    :var station_out: ID станции высадки
    :var station_out_name: Название станции высадки
    :var departure_time: Время отправления (по умолчанию '2024-01-01 00:00:00')

    Returns:
        JsonResponse:
            Успех (200):
                - status: 'success'
                - message: Сообщение с деталями бронирования
                - reservation_id: ID созданной брони
                - places: Список занятых мест
                - total_price: Общая стоимость
                - new_balance: Новый баланс пользователя
            Ошибка (400):
                - status: 'error'
                - message: Описание ошибки
        """
    user_id = request.GET.get('username', '')
    train_number = request.GET.get('train_id', '')
    seats = request.GET.get('seats', '')
    station_in_id = request.GET.get('station_in', '')
    station_out_id = request.GET.get('station_out', '')
    station_in_name = request.GET.get('station_in_name', '')
    station_out_name = request.GET.get('station_out_name', '')
    departure_time = request.GET.get('departure_time', '')

    if not user_id or not train_number or not seats:
        return JsonResponse({
            'status': 'error',
            'message': 'Недостаточно данных для бронирования'
        }, status=400)

    try:
        profile = Profile.objects.get(user__id=user_id)
        user = profile.user

        if station_in_id:
            station_in = Station.objects.get(station_id=station_in_id)
        elif station_in_name:
            station_in, _ = Station.objects.get_or_create(name=station_in_name)
        else:
            return JsonResponse({'status': 'error', 'message': 'Не указана станция отправления'}, status=400)

        if station_out_id:
            station_out = Station.objects.get(station_id=station_out_id)
        elif station_out_name:
            station_out, _ = Station.objects.get_or_create(name=station_out_name)
        else:
            return JsonResponse({'status': 'error', 'message': 'Не указана станция назначения'}, status=400)

        train = None

        all_trains = Train.objects.all()
        for t in all_trains:
            try:
                path_data = json.loads(t.path) if t.path else {}
                if str(path_data.get('number', '')) == str(train_number):
                    train = t
                    break
            except:
                pass

        if not train:
            train = Train.objects.create(
                id_station_start=station_in,
                id_station_stop=station_out,
                station_at_time=departure_time or '2024-01-01 00:00:00',
                path=json.dumps({'number': train_number})
            )
            print(f"Создан новый поезд #{train.train_id} с номером {train_number}")

    except Profile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Ошибка: {str(e)}'}, status=400)

    booked_seats = []
    place_nums = []
    PRICE_PER_SEAT = Money(2, 'USD')
    total_price = Money(0, 'USD')

    for item in seats.split('W'):
        if item and 'x' in item:
            carriage_num = item.split('x')[0]
            seat_num = item.split('x')[1]
            place_num = f"{carriage_num}-{seat_num}"

            if Reservation.objects.filter(train=train, place_num=place_num, status='active').exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'Место {seat_num} в вагоне {carriage_num} уже занято'
                }, status=400)

            booked_seats.append({
                'carriage': carriage_num,
                'seat': seat_num,
                'place_num': place_num
            })
            place_nums.append(place_num)
            total_price += PRICE_PER_SEAT

    if profile.balance < total_price:
        return JsonResponse({
            'status': 'error',
            'message': f'Недостаточно средств. Баланс: ${profile.balance.amount:.2f}, нужно: ${total_price.amount:.2f}'
        }, status=400)

    profile.balance -= total_price
    profile.save()

    reservation = Reservation.objects.create(
        user=user,
        train=train,
        place_num=', '.join(place_nums),
        station_in=station_in,
        station_out=station_out,
        status='active'
    )

    seats_list = ', '.join(place_nums)

    return JsonResponse({
        'status': 'success',
        'message': f'Бронирование #{reservation.reservation_id} оформлено! Места: {seats_list}. Сумма: ${total_price.amount:.2f}',
        'reservation_id': reservation.reservation_id,
        'places': place_nums,
        'total_price': str(total_price.amount),
        'new_balance': str(profile.balance.amount)
    }, status=200)