from typing import Tuple

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace, MatcherAdv

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1

LineMatcher = MatcherWTrace[LineMatcherLine]

LineMatcherAdv = MatcherAdv[LineMatcherLine]

LineMatcherDdv = MatcherDdv[LineMatcherLine]

LineMatcherSdv = MatcherSdv[LineMatcherLine]

FIRST_LINE_NUMBER_DESCRIPTION = 'Line numbers start at {}.'.format(FIRST_LINE_NUMBER)
