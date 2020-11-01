from typing import Tuple

from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1

LineMatcher = MatcherWTrace[LineMatcherLine]

FIRST_LINE_NUMBER_DESCRIPTION = 'Line numbers start at {}.'.format(FIRST_LINE_NUMBER)
