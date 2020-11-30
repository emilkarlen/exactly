from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher import MatcherSdv
from exactly_lib.type_val_prims.string_model.string_model import StringModel

StringMatcherAdv = MatcherAdv[StringModel]
StringMatcherDdv = MatcherDdv[StringModel]
StringMatcherSdv = MatcherSdv[StringModel]
