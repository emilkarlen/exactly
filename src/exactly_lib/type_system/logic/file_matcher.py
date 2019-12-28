from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv, MatcherAdv


class FileMatcherModel(ABC):
    @property
    @abstractmethod
    def path(self) -> DescribedPath:
        """Path of the file to match. May or may not exist."""
        pass


FileMatcher = MatcherWTraceAndNegation[FileMatcherModel]

FileMatcherAdv = MatcherAdv[FileMatcherModel]

FileMatcherDdv = MatcherDdv[FileMatcherModel]

FileMatcherSdvType = MatcherSdv[FileMatcherModel]
