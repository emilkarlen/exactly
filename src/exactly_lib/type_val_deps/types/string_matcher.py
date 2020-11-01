from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv

StringMatcherAdv = MatcherAdv[StringModel]
StringMatcherDdv = MatcherDdv[StringModel]
StringMatcherSdv = MatcherSdv[StringModel]
