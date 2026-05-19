from .get_attributes import get_attributes
from djmoney.money import Money


def repetitive_handler(request):
    (
        departure_time,
        seats,
        station_in_id,
        station_in_name,
        station_out_id,
        station_out_name,
        train_number,
        user_id,
        repetitive,
    ) = get_attributes(request)
