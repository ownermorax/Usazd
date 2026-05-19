def load_train_stations():
    from pathlib import Path
    from django.conf import settings
    import json
    from .small_func import simplify_station_name

    project_root = Path(settings.BASE_DIR)
    stations_path = project_root / "stations.json"

    if not stations_path.exists():
        return {}

    try:
        with open(stations_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            stations = {}
            simplified_stations = {}

            if isinstance(data, dict) and "countries" in data:
                for country in data["countries"]:
                    if "regions" in country:
                        for region in country["regions"]:
                            if "settlements" in region:
                                for settlement in region["settlements"]:
                                    if "stations" in settlement:
                                        for station in settlement["stations"]:
                                            transport_type = station.get(
                                                "transport_type", ""
                                            )
                                            if transport_type == "train":
                                                title = station.get("title", "")
                                                yandex_code = station.get(
                                                    "codes", {}
                                                ).get("yandex_code", "")
                                                if title and yandex_code:
                                                    stations[title.lower()] = {
                                                        "title": title,
                                                        "code": yandex_code,
                                                    }

                                                    simplified = simplify_station_name(
                                                        title
                                                    )
                                                    if (
                                                        simplified
                                                        and simplified
                                                        not in simplified_stations
                                                    ):
                                                        simplified_stations[
                                                            simplified
                                                        ] = {
                                                            "title": title,
                                                            "code": yandex_code,
                                                        }

            stations.update(simplified_stations)
            return stations
    except Exception as e:
        return {}
