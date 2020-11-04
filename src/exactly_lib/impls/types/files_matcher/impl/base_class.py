from abc import ABC

from exactly_lib.impls.types.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel


class FilesMatcherImplBase(MatcherImplBase[FilesMatcherModel], ABC):
    pass


class FilesMatcherDdvImplBase(MatcherDdv[FilesMatcherModel], ABC):
    pass


class FilesMatcherAdvImplBase(MatcherAdv[FilesMatcherModel], ABC):
    pass
