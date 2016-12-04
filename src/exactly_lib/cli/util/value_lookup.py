class NoMatchError(LookupError):
    pass


class MultipleMatchesError(LookupError):
    def __init__(self, matching_key_values: list):
        self.matching_key_values = matching_key_values


def lookup(key_pattern: str, key_value_iter: iter):
    """
    Looks up a value from a sequence of (key,value) pairs.

    :param key_pattern: str to look for, either as sub string, or as identical.
    :param key_value_iter: iterable of (key, value) paris
    :return: The value for the key that matches. If a key is found that is identical to key_pattern,
    then the value associated with that key is returned. If no key is identical, but one, and only one,
    key contains key_pattern as a sub string, then the associated value is returned.
    """
    matches = []
    for key, value in key_value_iter:
        if key_pattern == key:
            return value
        if key_pattern in key:
            matches.append((key, value))
    num_matches = len(matches)
    if num_matches == 0:
        raise NoMatchError()
    if num_matches == 1:
        return matches[0][1]
    raise MultipleMatchesError(matches)
