def format_trains_response(trains_data, from_station_title, to_station_title, date):
    from .get_last_result import get_last_result
    from .small_func import simplify_station_name_for_display

    if not trains_data or isinstance(trains_data, str):
        return None

    if "segments" not in trains_data:
        return None

    segments = trains_data.get("segments", [])

    if not segments:
        return f"На {date} поездов из {from_station_title} в {to_station_title} не найдено."

    max_trains = 3
    response_parts = [
        f"Расписание поездов из {from_station_title} в {to_station_title} на {date}:"
    ]
    response_parts.append("")

    for i, segment in enumerate(segments[:max_trains], 1):
        thread = segment.get("thread", {})
        train_name = thread.get("title", "Поезд")
        number = thread.get("number", "")

        departure = segment.get("departure", "")
        arrival = segment.get("arrival", "")

        dep_time = departure.split("T")[1][:5] if "T" in departure else departure
        arr_time = arrival.split("T")[1][:5] if "T" in arrival else arrival

        duration = segment.get("duration", 0)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        duration_str = f"{hours}ч {minutes}мин" if hours > 0 else f"{minutes}мин"

        from_station_display = simplify_station_name_for_display(
            segment.get("from", {}).get("title", from_station_title)
        )
        to_station_display = simplify_station_name_for_display(
            segment.get("to", {}).get("title", to_station_title)
        )

        response_parts.append(
            f"{i}. {train_name} {number}: {from_station_display} -> {to_station_display}"
        )
        response_parts.append(
            f"   Отправление: {dep_time}, Прибытие: {arr_time}, В пути: {duration_str}"
        )
        response_parts.append("")

    if len(segments) > max_trains:
        response_parts.append(
            f"* Показаны первые {max_trains} поезда из {len(segments)}"
        )

    return "\n".join(response_parts)
