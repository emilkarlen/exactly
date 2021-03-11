from abc import ABC

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv, FilesSourceAdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class FilesSourceAdvTestImpl(FilesSourceAdv, ABC):
    pass


class FilesSourceDdvTestImpl(FilesSourceDdv, ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.String(type(self))


class FilesSourceAdvConstantTestImpl(FilesSourceAdvTestImpl):
    def __init__(self, files: FilesSource):
        self._files = files

    def primitive(self, environment: ApplicationEnvironment) -> FilesSource:
        return self._files


class FilesSourceDdvConstantPrimitiveTestImpl(FilesSourceDdvTestImpl):
    def __init__(self, files: FilesSource):
        self._files = files

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[FilesSource]:
        return FilesSourceAdvConstantTestImpl(self._files)


class FilesSourceDdvWoResolvingTestImpl(FilesSourceDdvTestImpl):
    """A test impl StringSourceDdv that do not support resolving (to ADV)."""

    def __init__(self, validator: DdvValidator):
        self._validator = validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> FilesSourceAdv:
        raise NotImplementedError('unsupported')

    @property
    def validator(self) -> DdvValidator:
        return self._validator
