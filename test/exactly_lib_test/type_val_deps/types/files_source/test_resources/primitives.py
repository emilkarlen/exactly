from abc import ABC

from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements


class FilesSourceTestImpl(FilesSource, ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.String(type(self))


class FilesSourceThatDoesNothingTestImpl(FilesSourceTestImpl):
    def populate(self, directory: DescribedPath):
        pass


class FilesSourceThatWritesFileSystemElements(FilesSourceTestImpl):
    def __init__(self, contents: FileSystemElements):
        self._contents = contents

    def populate(self, directory: DescribedPath):
        fs.DirContents(self._contents).write_to(directory.primitive)
