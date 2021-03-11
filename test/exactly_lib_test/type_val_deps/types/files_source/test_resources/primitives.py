from abc import ABC

from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class FilesSourceTestImpl(FilesSource, ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.String(type(self))


class FilesSourceThatDoesNothingTestImpl(FilesSourceTestImpl):
    def populate(self, directory: DescribedPath):
        pass
