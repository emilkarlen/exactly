from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv

FileMatcherAdv = MatcherAdv[FileMatcherModel]
FileMatcherDdv = MatcherDdv[FileMatcherModel]
FileMatcherSdv = MatcherSdv[FileMatcherModel]
