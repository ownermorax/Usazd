def extract_resources_from_query(query, stations_dict):
    from .get_last_result import get_last_result
    from .small_func import (
        get_stop_words,
        get_init_result,
        get_word_matches,
        if_second_matches,
        get_second_atr,
        get_best_result,
        if_first_matches,
        get_date_patterns,
        get_time,
        get_another_result,
    )
    import re

    query_lower = query.lower()
    query_words = query_lower.split()

    stop_words = get_stop_words()
    query_words = [w for w in query_words if w not in stop_words]

    result = get_init_result()

    if len(query_words) < 1:
        return result

    word_matches = {}

    get_word_matches(query_words, stations_dict, word_matches)

    if len(query_words) == 1:
        word = query_words[0]
        if word in word_matches and len(word_matches[word]) > 0:
            if_second_matches(result, word_matches[word])

    elif len(query_words) >= 2:
        first_matches, second_matches = get_second_atr(query_words, word_matches)

        if first_matches and second_matches:
            get_best_result(first_matches, result, second_matches)

        elif first_matches and not second_matches:
            if_first_matches(first_matches, result)

        elif second_matches and not first_matches:
            if_second_matches(result, second_matches)

        get_last_result(result, word_matches)

    date_patterns = get_date_patterns()

    for pattern in date_patterns:
        match = re.search(pattern, query)
        if match:
            result["date"] = match.group()
            break

    if not result["date"]:
        get_time(result)

    get_another_result(query_lower, result)

    return result
