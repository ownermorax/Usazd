from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from .forms import ReservationForm

@login_required
def create_repeat_reservation(request):
    """
    Создание бронирования с возможностью повторения.

    :param request: HTTP запрос
    :return: страница с формой или перенаправление
    """
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()

            if reservation.repeat_type != 'none' and reservation.repeat_end_date:
                parent = reservation
                current_date = reservation.reservation_date
                while current_date < reservation.repeat_end_date:
                    if reservation.repeat_type == 'daily':
                        current_date += timedelta(days=1)
                    elif reservation.repeat_type == 'weekly':
                        current_date += timedelta(weeks=1)
                    elif reservation.repeat_type == 'monthly':
                        current_date += timedelta(days=30)
                    if current_date > reservation.repeat_end_date:
                        break
                    Reservation.objects.create(
                        user=request.user,
                        train=reservation.train,
                        place_num=reservation.place_num,
                        station_in=reservation.station_in,
                        station_out=reservation.station_out,
                        repeat_type='none',
                        parent_reservation=parent
                    )
            return redirect('active_reservations')
    else:
        form = ReservationForm()
    return render(request, 'create_reservation.html', {'form': form})