from abc import ABC, abstractmethod
from pathlib import Path

from exactly_lib.definitions import file_ref
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForResolver, PathDescriberForValue, \
    PathDescriberForPrimitive
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class DescribedPathPrimitive(ABC):
    @property
    @abstractmethod
    def primitive(self) -> Path:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        pass

    @abstractmethod
    def child(self, child_path_component: str) -> 'DescribedPathPrimitive':
        pass


class DescribedPathValue(ABC):
    """
    A FileRef, together with a description,
    and ability to resolve a corresponding object for the primitive value.
    """

    @property
    @abstractmethod
    def value(self) -> FileRef:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForValue:
        pass

    @abstractmethod
    def value_when_no_dir_dependencies(self) -> DescribedPathPrimitive:
        pass

    @abstractmethod
    def value_pre_sds(self, hds: HomeDirectoryStructure) -> DescribedPathPrimitive:
        pass

    @abstractmethod
    def value_post_sds(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        pass

    def value_post_sds__wo_hds(self, sds: SandboxDirectoryStructure) -> DescribedPathPrimitive:
        return self.value_post_sds(HomeAndSds(_DUMMY_HDS,
                                              sds))

    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        pass


class DescribedPathResolver(ABC):
    """
    A resolver of a FileRef, together with a description,
    and ability to resolve a corresponding object for the resolved value.
    """

    @property
    @abstractmethod
    def resolver(self) -> FileRefResolver:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForResolver:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> DescribedPathValue:
        pass


_DUMMY_HDS = HomeDirectoryStructure(
    Path(file_ref.EXACTLY_DIR__REL_HOME_CASE),
    Path(file_ref.EXACTLY_DIR__REL_HOME_ACT),
)
