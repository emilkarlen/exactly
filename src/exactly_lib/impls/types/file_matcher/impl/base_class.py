from abc import ABC

from exactly_lib.impls.types.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel


class FileMatcherImplBase(MatcherImplBase[FileMatcherModel], ABC):
    pass


class FileMatcherSdvImplBase(MatcherSdv[FileMatcherModel], ABC):
    pass


class FileMatcherDdvImplBase(MatcherDdv[FileMatcherModel], ABC):
    pass


class FileMatcherAdvImplBase(MatcherAdv[FileMatcherModel], ABC):
    pass
