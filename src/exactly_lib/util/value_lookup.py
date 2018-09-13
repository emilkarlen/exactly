from typing import Tuple, Iterable, TypeVar, Generic, Any, List


class NoMatchError(LookupError):
    pass


class MultipleMatchesError(LookupError):
    def __init__(self, matching_key_values: List[Tuple[str, Any]]):
        self.matching_key_values = matching_key_values


T = TypeVar('T')


class Match(Generic[T]):
    def __init__(self,
                 key: str,
                 value: T,
                 is_exact_match: bool):
        self._key = key
        self._value = value
        self._is_exact_match = is_exact_match

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> T:
        return self._value

    @property
    def is_exact_match(self) -> bool:
        return self._is_exact_match


def lookup(key_pattern: str, key_value_iter: Iterable[Tuple[str, T]]) -> Match[T]:
    """
    Looks up a value from a sequence of (key,value) pairs.

    :param key_pattern: str to look for, either as sub string, or as identical.
    :return: The value for the key that matches. If a key is found that is identical to key_pattern,
    then the value associated with that key is returned. If no key is identical, but one, and only one,
    key contains key_pattern as a sub string, then the associated value is returned.
    """
    upper_key_pattern = key_pattern.upper()
    matches = []
    for key, value in key_value_iter:
        upper_key = key.upper()
        if upper_key_pattern == upper_key:
            return Match(key, value, True)
        if upper_key_pattern in upper_key:
            matches.append((key, value))
    num_matches = len(matches)
    if num_matches == 0:
        raise NoMatchError()
    if num_matches == 1:
        match = matches[0]
        return Match(match[0], match[1], False)
    raise MultipleMatchesError(matches)
