"""
FilesCondition - a set of file names, each with an optional `FileMatcher`.
"""
from abc import ABC, abstractmethod
from pathlib import PurePosixPath
from typing import Optional, Mapping

from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher


class FilesCondition(WithDetailsDescription, ABC):
    @property
    @abstractmethod
    def files(self) -> Mapping[PurePosixPath, Optional[FileMatcher]]:
        pass
