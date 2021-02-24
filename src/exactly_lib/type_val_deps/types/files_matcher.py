from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel

FilesMatcherAdv = MatcherAdv[FilesMatcherModel]
FilesMatcherDdv = MatcherDdv[FilesMatcherModel]
FilesMatcherSdv = MatcherSdv[FilesMatcherModel]
