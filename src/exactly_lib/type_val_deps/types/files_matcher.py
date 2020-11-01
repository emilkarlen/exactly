from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv

FilesMatcherAdv = MatcherAdv[FilesMatcherModel]
FilesMatcherDdv = MatcherDdv[FilesMatcherModel]
FilesMatcherSdv = MatcherSdv[FilesMatcherModel]
