from abc import ABC

from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv


class FilesMatcherImplBase(MatcherImplBase[FilesMatcherModel], ABC):
    pass


class FilesMatcherDdvImplBase(MatcherDdv[FilesMatcherModel], ABC):
    pass


class FilesMatcherAdvImplBase(MatcherAdv[FilesMatcherModel], ABC):
    pass
