from abc import ABC

from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv


class FileMatcherImplBase(MatcherImplBase[FileMatcherModel], ABC):
    pass


class FileMatcherDdvImplBase(MatcherDdv[FileMatcherModel], ABC):
    pass
