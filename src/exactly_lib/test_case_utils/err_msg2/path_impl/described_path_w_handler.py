from abc import ABC, abstractmethod

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathValue, DescribedPathPrimitive, \
    DescribedPathResolver
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForResolver, PathDescriberForValue, \
    PathDescriberForPrimitive
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.symbol_table import SymbolTable


class PathDescriberHandlerForResolver(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForResolver:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> 'PathDescriberHandlerForValue':
        pass


class PathDescriberHandlerForValue(ABC):
    @property
    @abstractmethod
    def describer(self) -> PathDescriberForValue:
        pass

    @abstractmethod
    def value_when_no_dir_dependencies(self) -> 'PathDescriberForPrimitive':
        pass

    @abstractmethod
    def value_pre_sds(self, hds: HomeDirectoryStructure) -> 'PathDescriberForPrimitive':
        pass

    @abstractmethod
    def value_post_sds(self, tcds: HomeAndSds) -> 'PathDescriberForPrimitive':
        pass

    @abstractmethod
    def value_of_any_dependency(self, tcds: HomeAndSds) -> 'PathDescriberForPrimitive':
        pass


class DescribedPathValueWHandler(DescribedPathValue):
    def __init__(self,
                 path_value: FileRef,
                 describer_handler: PathDescriberHandlerForValue
                 ):
        self._path_value = path_value
        self._describer_handler = describer_handler

    @property
    def value(self) -> FileRef:
        return self._path_value

    @property
    def describer(self) -> PathDescriberForValue:
        return self._describer_handler.describer

    def value_when_no_dir_dependencies(self) -> DescribedPathPrimitive:
        return DescribedPathPrimitive(
            self._path_value.value_when_no_dir_dependencies(),
            self._describer_handler.value_when_no_dir_dependencies(),
        )

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> DescribedPathPrimitive:
        return DescribedPathPrimitive(
            self._path_value.value_pre_sds(hds),
            self._describer_handler.value_pre_sds(hds),
        )

    def value_post_sds(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        return DescribedPathPrimitive(
            self._path_value.value_post_sds(tcds.sds),
            self._describer_handler.value_post_sds(tcds),
        )

    def value_of_any_dependency(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        return DescribedPathPrimitive(
            self._path_value.value_of_any_dependency(tcds),
            self._describer_handler.value_of_any_dependency(tcds),
        )


class DescribedPathResolverWHandler(DescribedPathResolver):
    def __init__(self,
                 path: FileRefResolver,
                 describer_handler: PathDescriberHandlerForResolver):
        self._path = path
        self._describer_handler = describer_handler

    @property
    def resolver(self) -> FileRefResolver:
        return self._path

    @property
    def describer(self) -> PathDescriberForResolver:
        return self._describer_handler.describer

    def resolve(self, symbols: SymbolTable) -> DescribedPathValue:
        return DescribedPathValueWHandler(
            self._path.resolve(symbols),
            self._describer_handler.resolve(symbols),
        )
