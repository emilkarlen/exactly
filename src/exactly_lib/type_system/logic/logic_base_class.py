from abc import abstractmethod, ABC
from typing import TypeVar, Generic

from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.util.file_utils import TmpDirFileSpace


class ApplicationEnvironment:
    def __init__(self,
                 tmp_files_space: TmpDirFileSpace,
                 ):
        self._tmp_files_space = tmp_files_space

    @property
    def tmp_files_space(self) -> TmpDirFileSpace:
        return self._tmp_files_space


VALUE_TYPE = TypeVar('VALUE_TYPE')


class ApplicationEnvironmentDependentValue(Generic[VALUE_TYPE], ABC):
    """A value that may depend on :class:`ApplicationEnvironment`"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> VALUE_TYPE:
        pass


class LogicDdv(Generic[VALUE_TYPE],
               DirDependentValue[ApplicationEnvironmentDependentValue[VALUE_TYPE]],
               ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[VALUE_TYPE]:
        pass


class LogicWithStructureDdv(Generic[VALUE_TYPE],
                            LogicDdv[VALUE_TYPE],
                            WithTreeStructureDescription,
                            ABC):
    """A :class:`LogicDdv` that can report its structure"""
    pass
