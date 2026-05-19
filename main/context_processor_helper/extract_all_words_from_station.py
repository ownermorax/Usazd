def extract_all_words_from_station(station_title):
    from .extract_resources_from_query import extract_resources_from_query
    from .small_func import normalize_text
    import re

    words = []

    match = re.match(r"^(.*?)\s*\(([^)]+)\)$", station_title)
    if match:
        main_part = match.group(1).strip()
        bracket_part = match.group(2).strip()

        main_words = main_part.split()
        bracket_words = bracket_part.split()

        words.extend(main_words)
        words.extend(bracket_words)
    else:
        words = station_title.split()

    words = [normalize_text(w) for w in words if w.lower() not in ["вокзал", "станция"]]

    return words
