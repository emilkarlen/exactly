from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, \
    MatcherAdv, MatcherWTrace
from exactly_lib.type_system.logic.string_model import StringModel

StringMatcher = MatcherWTrace[StringModel]

StringMatcherAdv = MatcherAdv[StringModel]

StringMatcherDdv = MatcherDdv[StringModel]

StringMatcherSdv = MatcherSdv[StringModel]
