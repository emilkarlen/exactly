from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List

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
from exactly_lib.type_system.data import concrete_path_parts
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.symbol_table import SymbolTable


class _ResolverDescriber(Renderer[str]):
    """Handles description of a resolver, together with func for computing children etc."""

    def __init__(self,
                 path_resolver: FileRefResolver,
                 suffixes: List[str],
                 ):
        self.path_resolver = path_resolver
        self.suffixes = suffixes

    def render(self) -> str:
        resolver_str = path_resolver_str_renderers.new_std(self.path_resolver).render()
        return '/'.join([resolver_str] + self.suffixes)

    def child(self, child_path_component: str) -> '_ResolverDescriber':
        return _ResolverDescriber(
            self.path_resolver,
            self.suffixes + [child_path_component]
        )


class PathDescriberHandlerForResolverWithResolver(PathDescriberHandlerForResolver):
    def __init__(self,
                 path_resolver: FileRefResolver,
                 ):
        self._path_resolver = path_resolver

    @property
    def describer(self) -> PathDescriberForResolver:
        return _from_str.PathDescriberForResolverFromStr(
            _ResolverDescriber(self._path_resolver, [])
        )

    def resolve(self, resolved_value: FileRef, symbols: SymbolTable) -> PathDescriberHandlerForValue:
        return PathDescriberHandlerForValueWithValue(
            _ResolverDescriber(self._path_resolver, []),
            resolved_value,
        )


class PathManipulationFunctionalityForFixedValue(PathDescriberForValue, ABC):
    """
    A resolver + value that has been fixed by symbols and TCDS.

    Used by objects representing a primitive value.
    Acts as a helper for functionality of the path manipulations
    supported by primitive value handlers
    (child, parent).
    """

    def __init__(self,
                 resolver_describer: _ResolverDescriber,
                 value: FileRef,
                 ):
        self._resolver_describer = resolver_describer
        self._value = value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._value.resolving_dependency()

    @property
    def resolver(self) -> Renderer[str]:
        return self._resolver_describer

    @abstractmethod
    def child(self, child_path_component: str) -> 'PathManipulationFunctionalityForFixedValue':
        pass

    def _child_value(self, child_path_component: str) -> FileRef:
        return file_refs.stacked(
            self._value,
            concrete_path_parts.PathPartAsFixedPath(child_path_component),
        )

    def _child_resolver(self, child_path_component: str) -> _ResolverDescriber:
        return self._resolver_describer.child(child_path_component)


class PathDescriberHandlerForValueWithValue(PathDescriberHandlerForValue):
    def __init__(self,
                 resolver_describer: _ResolverDescriber,
                 path_value: FileRef,
                 ):
        self._cwd = None
        self._resolver_describer = resolver_describer
        self._path_value = path_value
        self._relativity_type = path_value.relativity().relativity_type
        if self._relativity_type is RelOptionType.REL_CWD:
            self._cwd = Path().cwd()

    @property
    def describer(self) -> PathDescriberForValue:
        return _from_str.PathDescriberForValueFromStr(
            self._resolver_describer,
            self._value_renderer_before_fixation(),
            self._resolving_dependency,
        )

    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._resolver_describer,
                self._path_value,
            ),
        )

    def value_pre_sds(self, primitive: Path, hds: HomeDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._resolver_describer,
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
                self._resolver_describer,
                self._path_value,
                tcds,
                self._cwd,
            )
        else:
            return PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._resolver_describer,
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
                 resolver_describer: _ResolverDescriber,
                 value: FileRef,
                 ):
        super().__init__(resolver_describer, value)

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

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForNotRelCwd(
            self._child_resolver(child_path_component),
            self._child_value(child_path_component),
        )


class PathManipulationFunctionalityForFixedValueForRelCwd(PathManipulationFunctionalityForFixedValue):
    def __init__(self,
                 resolver_describer: _ResolverDescriber,
                 value: FileRef,
                 tcds: HomeAndSds,
                 cwd: Path,
                 ):
        super().__init__(resolver_describer, value)
        self._tcds = tcds
        self._cwd = cwd

    @property
    def value(self) -> Renderer[str]:
        return path_value_str_renderers.PathValueRelCwd(self._value,
                                                        self._cwd,
                                                        self._tcds)

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForRelCwd(
            self._child_resolver(child_path_component),
            self._child_value(child_path_component),
            self._tcds,
            self._cwd,
        )


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

    def child(self, child_path: Path, child_path_component: str) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            child_path,
            self._fixed_value.child(child_path_component),
        )
