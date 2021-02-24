from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine

LineMatcherAdv = MatcherAdv[LineMatcherLine]
LineMatcherDdv = MatcherDdv[LineMatcherLine]
LineMatcherSdv = MatcherSdv[LineMatcherLine]
