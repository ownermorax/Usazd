def calculate_similarity_score(query_word, station_info):
    """Вычисляет оценку схожести между словом запроса и информацией о станции."""
    from .calculate_word_similarity import calculate_word_similarity
    from .extract_all_words_from_station import extract_all_words_from_station
    from .small_func import normalize_text

    query_word = normalize_text(query_word)
    station_title = normalize_text(station_info["title"])

    station_words = extract_all_words_from_station(station_info["title"])

    if not station_words:
        return 0.0

    best_score = 0.0

    for sw in station_words:
        if len(sw) < 2:
            continue
        word_score = calculate_word_similarity(query_word, sw)
        if word_score > best_score:
            best_score = word_score

    return best_score
