def get_last_result(result, word_matches):
    """Заполняет результат последними найденными совпадениями станций."""
    if not result["from_station"] and not result["to_station"]:
        all_matches = []
        for word, matches in word_matches.items():
            for score, station in matches:
                all_matches.append((score, station))

        all_matches.sort(key=lambda x: x[0], reverse=True)

        if len(all_matches) >= 2:
            result["from_station"] = all_matches[0][1]["title"].lower()
            result["from_station_code"] = all_matches[0][1]["code"]
            result["from_station_title"] = all_matches[0][1]["title"]

            for score, station in all_matches[1:]:
                if station["title"].lower() != result["from_station"]:
                    result["to_station"] = station["title"].lower()
                    result["to_station_code"] = station["code"]
                    result["to_station_title"] = station["title"]
                    break
        elif len(all_matches) == 1:
            result["to_station"] = all_matches[0][1]["title"].lower()
            result["to_station_code"] = all_matches[0][1]["code"]
            result["to_station_title"] = all_matches[0][1]["title"]
