from typing import Callable

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_matcher import FileToCheck, DestinationFilePathGetter
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand, TmpDirFileSpace
from exactly_lib_test.type_system.data.test_resources import described_path

ModelConstructor = Callable[[Tcds], FileToCheck]


class ModelBuilder:
    """Builder of :class:`FileToCheck` attributes."""

    def __init__(self):
        self.original_file_contents = ''

    def with_original_file_contents(self, contents: str):
        self.original_file_contents = contents
        return self


def empty_model() -> ModelBuilder:
    return ModelBuilder()


def model_of(contents: str) -> ModelBuilder:
    return ModelBuilder().with_original_file_contents(contents)


def arbitrary_model() -> ModelBuilder:
    return empty_model()


class ModelFromBuilder:
    """Constructs a :class:^FileToCheck^ given an environment with existing directories"""

    def __init__(self,
                 model_builder: ModelBuilder,
                 sds: SandboxDirectoryStructure):
        self.model_builder = model_builder
        self.sds = sds

    def construct(self) -> FileToCheck:
        tmp_dir_file_space = TmpDirFileSpaceAsDirCreatedOnDemand(self.sds.internal_tmp_dir)
        original_file_path = self._create_original_file(tmp_dir_file_space)

        return FileToCheck(
            original_file_path,
            IdentityStringTransformer(),
            DestinationFilePathGetter(),
        )

    def _create_original_file(self, file_space: TmpDirFileSpace) -> DescribedPath:
        original_file_path = file_space.new_path()

        with original_file_path.open(mode='w') as f:
            f.write(self.model_builder.original_file_contents)

        return described_path.new_primitive(original_file_path)
