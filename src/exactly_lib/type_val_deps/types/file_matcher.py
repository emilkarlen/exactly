from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel

FileMatcherAdv = MatcherAdv[FileMatcherModel]
FileMatcherDdv = MatcherDdv[FileMatcherModel]
FileMatcherSdv = MatcherSdv[FileMatcherModel]
