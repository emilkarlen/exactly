from abc import ABC

from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription


class FilesSource(WithDetailsDescription, ABC):
    """Populates a directory with files."""

    def populate(self, directory: DescribedPath):
        raise NotImplementedError('todo')
