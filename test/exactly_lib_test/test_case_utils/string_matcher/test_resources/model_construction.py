from typing import Callable

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_models.tmp_path_generators import PathGeneratorOfExclusiveDir
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.test_resources.string_models import of_string

ModelConstructor = Callable[[Tcds], StringModel]


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
                 sds: SandboxDirectoryStructure,
                 ):
        self.model_builder = model_builder
        self.sds = sds

    def construct(self) -> StringModel:
        return of_string(
            self.model_builder.original_file_contents,
            PathGeneratorOfExclusiveDir(
                self.sds.internal_tmp_dir / 'string-model-dir-for-test'
            )
        )
