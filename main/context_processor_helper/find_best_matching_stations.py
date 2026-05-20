def find_best_matching_stations(
    query_word, stations_dict, min_score=0.5, max_results=10
):
    """Находит лучшие соответствия станций по слову запроса."""
    from .calculate_word_similarity import calculate_word_similarity
    from .extract_resources_from_query import extract_resources_from_query
    from .station_matches_query_word import station_matches_query_word
    from .small_func import normalize_text
    from .calculate_similarity_score import calculate_similarity_score

    query_word = normalize_text(query_word)
    if not query_word or len(query_word) < 2:
        return []

    exact_matches = []
    for station_lower, station_info in stations_dict.items():
        if station_matches_query_word(station_info, query_word):
            exact_matches.append((1.0, station_info))

    if exact_matches:
        seen = set()
        unique_matches = []
        for score, station in exact_matches:
            if station["title"].lower() not in seen:
                seen.add(station["title"].lower())
                unique_matches.append((score, station))
        if unique_matches:
            return unique_matches[:max_results]

    scored_matches = []
    for station_lower, station_info in stations_dict.items():
        score = calculate_similarity_score(query_word, station_info)
        if score >= min_score:
            scored_matches.append((score, station_info))

    scored_matches.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    unique_matches = []
    for score, station in scored_matches:
        if station["title"].lower() not in seen:
            seen.add(station["title"].lower())
            unique_matches.append((score, station))

    return unique_matches[:max_results]
