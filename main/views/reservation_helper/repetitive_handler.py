from .get_attributes import *
from .repetitive_handler import *
from .get_attributes import *
from .get_some_atr import *
from .search_train import *
from .do_reservation import *
from .get_response import *

from django.http import JsonResponse
from djmoney.money import Money
from main.models import Profile, Station
from .get_attributes import *
from .repetitive_handler import *
from .get_attributes import *
from .get_some_atr import *
from .search_train import *
from .do_reservation import *
from .get_response import *


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
