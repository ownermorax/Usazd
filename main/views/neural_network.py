from django.shortcuts import render


def schedule_card(request, from_station, to_station):
    return render(
        request,
        "main/schedule_card.html",
        {
            "from_station": from_station,
            "to_station": to_station,
        },
    )


def quick_booking(request):
    return render(
        request,
        "main/quick_booking.html",
        {
            "from_station": request.GET.get("from", ""),
            "to_station": request.GET.get("to", ""),
            "date": request.GET.get("date", ""),
        },
    )
