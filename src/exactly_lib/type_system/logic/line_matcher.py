from typing import Tuple

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1

LineMatcher = MatcherWTrace[LineMatcherLine]

LineMatcherAdv = ApplicationEnvironmentDependentValue[LineMatcher]

LineMatcherDdv = MatcherDdv[LineMatcherLine]

LineMatcherSdv = MatcherSdv[LineMatcherLine]
