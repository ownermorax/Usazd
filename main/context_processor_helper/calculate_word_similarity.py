def calculate_word_similarity(query_word, station_word):
    """Вычисляет схожесть между двумя словами."""
    from .small_func import get_max_len, normalize_text

    if not query_word or not station_word:
        return 0.0

    query_word = normalize_text(query_word)
    station_word = normalize_text(station_word)

    if query_word == station_word:
        return 1.0

    if len(query_word) < 2 or len(station_word) < 2:
        return 0.0

    if query_word in station_word:
        if len(query_word) >= len(station_word) * 0.6:
            return 0.9
        else:
            return 0.0

    if station_word in query_word:
        if len(station_word) >= len(query_word) * 0.6:
            return 0.9
        else:
            return 0.0

    m = len(query_word)
    n = len(station_word)

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0

    max_len = get_max_len(dp, m, max_len, n, query_word, station_word)

    if max_len == 0:
        return 0.0

    if max_len < min(m, n) * 0.5:
        return 0.0

    if max_len < max(m, n) * 0.4:
        return 0.0

    ratio1 = max_len / m
    ratio2 = max_len / n

    avg_ratio = (ratio1 + ratio2) / 2

    return avg_ratio
