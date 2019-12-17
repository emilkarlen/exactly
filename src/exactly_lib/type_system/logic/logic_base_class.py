from abc import abstractmethod, ABC
from typing import TypeVar, Generic

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
    """Application Environment Dependent Matcher"""

    @abstractmethod
    def applier(self, environment: ApplicationEnvironment) -> VALUE_TYPE:
        pass


class LogicTypeDdv(Generic[VALUE_TYPE],
                   DirDependentValue[VALUE_TYPE],
                   WithTreeStructureDescription,
                   ABC):
    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[VALUE_TYPE]:
        pass
