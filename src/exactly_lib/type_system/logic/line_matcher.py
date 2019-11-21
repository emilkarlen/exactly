from typing import Tuple

from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1

LineMatcher = MatcherWTraceAndNegation[LineMatcherLine]

LineMatcherDdv = MatcherDdv[LineMatcherLine]
