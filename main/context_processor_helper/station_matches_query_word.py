def station_matches_query_word(station_info, query_word):
    """Проверяет, соответствует ли станция слову запроса."""
    from .extract_all_words_from_station import extract_all_words_from_station
    from .small_func import normalize_text

    query_word = normalize_text(query_word)
    if not query_word or len(query_word) < 2:
        return False

    station_title = normalize_text(station_info["title"])

    if f" {query_word} " in f" {station_title} ":
        return True

    station_words = extract_all_words_from_station(station_info["title"])
    for sw in station_words:
        if sw == query_word:
            return True

    return False
