from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource

StringMatcherAdv = MatcherAdv[StringSource]
StringMatcherDdv = MatcherDdv[StringSource]
StringMatcherSdv = MatcherSdv[StringSource]
