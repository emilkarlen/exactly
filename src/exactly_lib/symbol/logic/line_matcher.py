from exactly_lib.symbol.logic.matcher import MatcherSdv, MatcherTypeStv
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine


class LineMatcherStv(MatcherTypeStv[LineMatcherLine]):
    """ Base class for SDVs of :class:`LineMatcher`. """

    def __init__(self, matcher: MatcherSdv[LineMatcherLine]):
        self._matcher = matcher

    @property
    def as_generic(self) -> MatcherSdv[LineMatcherLine]:
        return self._matcher

    def value(self) -> MatcherSdv[LineMatcherLine]:
        return self._matcher
