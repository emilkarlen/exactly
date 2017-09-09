from exactly_lib.type_system.logic.matcher_base_class import Matcher


class LineMatcher(Matcher):
    """Matches text lines."""

    def matches(self, line: str) -> bool:
        raise NotImplementedError('abstract method')
