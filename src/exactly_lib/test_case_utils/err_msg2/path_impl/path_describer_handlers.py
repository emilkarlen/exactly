from abc import ABC
from pathlib import Path
from typing import Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForValue, PathDescriberForPrimitive, \
    PathDescriberForResolver
from exactly_lib.test_case_utils.err_msg2.path_impl import path_describer_from_str as _from_str
from exactly_lib.test_case_utils.err_msg2.path_impl import \
    path_primitive_str_renderers, path_value_str_renderers
from exactly_lib.test_case_utils.err_msg2.path_impl import path_resolver_str_renderers
from exactly_lib.test_case_utils.err_msg2.path_impl.described_path_w_handler import PathDescriberHandlerForValue, \
    PathDescriberHandlerForResolver, PathDescriberHandlerForPrimitive
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.symbol_table import SymbolTable


class PathDescriberHandlerForResolverWithResolver(PathDescriberHandlerForResolver):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 ):
        self._path_resolver = path_resolver

    @property
    def describer(self) -> PathDescriberForResolver:
        return _from_str.PathDescriberForResolverFromStr(
            path_resolver_str_renderers.new_std(self._path_resolver)
        )

    def resolve(self, resolved_value: FileRef, symbols: SymbolTable) -> PathDescriberHandlerForValue:
        return PathDescriberHandlerForValueWithValue(
            self._path_resolver,
            resolved_value,
        )


class PathManipulationFunctionalityForFixedValue(PathDescriberForValue, ABC):
    def __init__(self,
                 resolver: FileRefResolver,
                 value: FileRef,
                 ):
        self._resolver = resolver
        self._value = value

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._value.resolving_dependency()

    @property
    def resolver(self) -> Renderer[str]:
        return path_resolver_str_renderers.new_std(self._resolver)


class PathDescriberHandlerForValueWithValue(PathDescriberHandlerForValue):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 path_value: FileRef,
                 ):
        self._cwd = None
        self._path_resolver = path_resolver
        self._path_value = path_value
        self._relativity_type = path_value.relativity().relativity_type
        if self._relativity_type is RelOptionType.REL_CWD:
            self._cwd = Path().cwd()

    @property
    def describer(self) -> PathDescriberForValue:
        return _from_str.PathDescriberForValueFromStr(
            path_resolver_str_renderers.new_std(self._path_resolver),
            self._value_renderer_before_fixation(),
            self._resolving_dependency,
        )

    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_resolver,
                self._path_value,
            ),
        )

    def value_pre_sds(self, primitive: Path, hds: HomeDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_resolver,
                self._path_value,
            ),
        )

    def value_post_sds(self, primitive: Path, tcds: HomeAndSds) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            self._fixation(tcds),
        )

    def value_of_any_dependency(self, primitive: Path, tcds: HomeAndSds) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            self._fixation(tcds),
        )

    def _resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._path_value.resolving_dependency()

    def _fixation(self, tcds: HomeAndSds) -> PathManipulationFunctionalityForFixedValue:
        if self._relativity_type is RelOptionType.REL_CWD:
            return PathManipulationFunctionalityForFixedValueForRelCwd(
                self._path_resolver,
                self._path_value,
                tcds,
                self._cwd,
            )
        else:
            return PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_resolver,
                self._path_value,
            )

    def _value_renderer_before_fixation(self) -> Renderer[str]:
        relativity_type = self._relativity_type

        if relativity_type is RelOptionType.REL_CWD:
            return path_value_str_renderers.PathValueRelJustCwd(self._path_value,
                                                                self._cwd)

        if relativity_type is None:
            return path_value_str_renderers.PathValuePlainAbsolute(self._path_value)

        return path_value_str_renderers.PathValueRelTcdsDir(self._path_value)


class PathManipulationFunctionalityForFixedValueForNotRelCwd(PathManipulationFunctionalityForFixedValue):
    def __init__(self,
                 resolver: FileRefResolver,
                 value: FileRef,
                 ):
        super().__init__(resolver, value)

    @property
    def value(self) -> Renderer[str]:
        value = self._value
        relativity_type = value.relativity().relativity_type
        return (
            path_value_str_renderers.PathValuePlainAbsolute(value)
            if relativity_type is None
            else
            path_value_str_renderers.PathValueRelTcdsDir(value)
        )


class PathManipulationFunctionalityForFixedValueForRelCwd(PathManipulationFunctionalityForFixedValue):
    def __init__(self,
                 resolver: FileRefResolver,
                 value: FileRef,
                 tcds: HomeAndSds,
                 cwd: Path,
                 ):
        super().__init__(resolver, value)
        self._tcds = tcds
        self._cwd = cwd

    @property
    def value(self) -> Renderer[str]:
        return path_value_str_renderers.PathValueRelCwd(self._value,
                                                        self._cwd,
                                                        self._tcds)


class PathDescriberHandlerForPrimitiveWithPrimitive(PathDescriberHandlerForPrimitive):
    def __init__(self,
                 primitive: Path,
                 fixed_value: PathManipulationFunctionalityForFixedValue,
                 ):
        self._primitive = primitive
        self._fixed_value = fixed_value

    @property
    def describer(self) -> PathDescriberForPrimitive:
        return _from_str.PathDescriberForPrimitiveFromStr(
            self._fixed_value,
            path_primitive_str_renderers.Constant(self._primitive)
        )
