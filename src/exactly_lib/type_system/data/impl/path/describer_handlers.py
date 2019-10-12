import os.path
import pathlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from exactly_lib.definitions import file_ref
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, DirectoryStructurePartition, \
    SpecificPathRelativity
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import concrete_path_parts
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef, DescribedPathPrimitive
from exactly_lib.type_system.data.impl.path import described_w_handler
from exactly_lib.type_system.data.impl.path import value_str_renderers, primitive_str_renderers, \
    describer_from_str as _from_str
from exactly_lib.type_system.data.impl.path.described_w_handler import PathDescriberHandlerForValue, \
    PathDescriberHandlerForPrimitive
from exactly_lib.type_system.data.path_describer import PathDescriberForValue, PathDescriberForPrimitive
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer


class PathManipulationFunctionalityForFixedValue(PathDescriberForValue, ABC):
    """
    A resolver + value that has been fixed by symbols and TCDS.

    Used by objects representing a primitive value.
    Acts as a helper for functionality of the path manipulations
    supported by primitive value handlers
    (child, parent).
    """

    def __init__(self, value: FileRef):
        self._value = value

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._value.resolving_dependency()

    @abstractmethod
    def child(self, child_path_component: str) -> 'PathManipulationFunctionalityForFixedValue':
        pass

    @abstractmethod
    def parent(self) -> 'PathManipulationFunctionalityForFixedValue':
        pass

    def _child_value(self, child_path_component: str) -> FileRef:
        return file_refs.stacked(
            self._value,
            concrete_path_parts.PathPartAsFixedPath(child_path_component),
        )

    def _parent_value(self) -> FileRef:
        return _ParentFileRef(self._value)


class PathDescriberHandlerForValueWithValue(PathDescriberHandlerForValue):
    def __init__(self, path_value: FileRef):
        self._path_value = path_value
        self._relativity_type = path_value.relativity().relativity_type

    @property
    def describer(self) -> PathDescriberForValue:
        return _from_str.PathDescriberForValueFromStr(
            self._value_renderer_before_fixation(),
            self._resolving_dependency,
        )

    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_value,
            ),
        )

    def value_pre_sds(self, primitive: Path, hds: HomeDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_value,
            ),
        )

    def value_post_sds__wo_hds(self, primitive: Path,
                               sds: SandboxDirectoryStructure) -> PathDescriberHandlerForPrimitive:
        return self.value_post_sds(primitive, HomeAndSds(_DUMMY_HDS, sds))

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
                self._path_value,
                tcds,
                Path().cwd(),
            )
        else:
            return PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_value,
            )

    def _value_renderer_before_fixation(self) -> Renderer[str]:
        relativity_type = self._relativity_type

        if relativity_type is RelOptionType.REL_CWD:
            return value_str_renderers.PathValueRelUnknownCwd(self._path_value)
        elif relativity_type is None:
            return value_str_renderers.PathValuePlainAbsolute(self._path_value)
        else:
            return value_str_renderers.PathValueRelTcdsDir(self._path_value)


class PathManipulationFunctionalityForFixedValueForNotRelCwd(PathManipulationFunctionalityForFixedValue):
    def __init__(self, value: FileRef):
        super().__init__(value)

    @property
    def value(self) -> Renderer[str]:
        value = self._value
        relativity_type = value.relativity().relativity_type
        return (
            value_str_renderers.PathValuePlainAbsolute(value)
            if relativity_type is None
            else
            value_str_renderers.PathValueRelTcdsDir(value)
        )

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForNotRelCwd(
            self._child_value(child_path_component),
        )

    def parent(self) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForNotRelCwd(
            self._parent_value(),
        )


class PathManipulationFunctionalityForFixedValueForRelCwd(PathManipulationFunctionalityForFixedValue):
    def __init__(self,
                 value: FileRef,
                 tcds: HomeAndSds,
                 cwd: Optional[Path],
                 ):
        super().__init__(value)
        self._tcds = tcds
        self._cwd = cwd

    @property
    def value(self) -> Renderer[str]:
        return (
            value_str_renderers.PathValueRelUnknownCwd(self._value)
            if self._cwd is None
            else
            value_str_renderers.PathValueRelCwd(self._value, self._cwd, self._tcds)
        )

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForRelCwd(
            self._child_value(child_path_component),
            self._tcds,
            self._cwd,
        )

    def parent(self) -> PathManipulationFunctionalityForFixedValue:
        return PathManipulationFunctionalityForFixedValueForRelCwd(
            self._parent_value(),
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
            primitive_str_renderers.Constant(self._primitive)
        )

    def child(self, child_path: Path, child_path_component: str) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            child_path,
            self._fixed_value.child(child_path_component),
        )

    def parent(self, parent_path: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            parent_path,
            self._fixed_value.parent(),
        )


class _ParentFileRef(FileRef):
    def __init__(self, original: FileRef):
        self._original = original
        self._value = None

    def path_suffix(self) -> PathPart:
        return self._get_value().path_suffix()

    def path_suffix_str(self) -> str:
        return self._get_value().path_suffix_str()

    def path_suffix_path(self) -> pathlib.Path:
        return self._get_value().path_suffix_path()

    def relativity(self) -> SpecificPathRelativity:
        return self._get_value().relativity()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        return self._get_value().value_when_no_dir_dependencies()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self._get_value().value_pre_sds(hds)

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self._get_value().value_post_sds(sds)

    def describer(self) -> PathDescriberForValue:
        return self._describer_handler().describer

    def value_when_no_dir_dependencies__d(self) -> DescribedPathPrimitive:
        primitive = self.value_when_no_dir_dependencies()
        return described_w_handler.DescribedPathPrimitiveWHandler(
            primitive,
            self._describer_handler().value_when_no_dir_dependencies(primitive),
        )

    def value_pre_sds__d(self, hds: HomeDirectoryStructure) -> DescribedPathPrimitive:
        primitive = self.value_pre_sds(hds)
        return described_w_handler.DescribedPathPrimitiveWHandler(
            primitive,
            self._describer_handler().value_pre_sds(primitive, hds),
        )

    def value_post_sds__d(self, sds: SandboxDirectoryStructure) -> DescribedPathPrimitive:
        primitive = self.value_post_sds(sds)
        return described_w_handler.DescribedPathPrimitiveWHandler(
            primitive,
            self._describer_handler().value_post_sds__wo_hds(primitive, sds),
        )

    def value_of_any_dependency__d(self, tcds: HomeAndSds) -> DescribedPathPrimitive:
        primitive = self.value_of_any_dependency(tcds)
        return described_w_handler.DescribedPathPrimitiveWHandler(
            primitive,
            self._describer_handler().value_of_any_dependency(primitive, tcds),
        )

    def _describer_handler(self) -> PathDescriberHandlerForValue:
        return PathDescriberHandlerForValueWithValue(self)

    def _get_value(self) -> FileRef:
        if self._value is None:
            value = self._value
            path_suffix = self._parent_path_suffix(value.path_suffix().value())
            relativity = value.relativity()
            self._value = (
                file_refs.absolute_part(path_suffix)
                if relativity.is_absolute
                else
                file_refs.of_rel_option(relativity.relativity_type,
                                        path_suffix)
            )

        return self._value

    @staticmethod
    def _parent_path_suffix(path_suffix: str) -> PathPart:
        if path_suffix == '':
            return file_refs.constant_path_part('..')

        (head, tail) = os.path.split(path_suffix)

        return file_refs.constant_path_part(head)


_DUMMY_HDS = HomeDirectoryStructure(
    pathlib.Path(file_ref.EXACTLY_DIR__REL_HOME_CASE),
    pathlib.Path(file_ref.EXACTLY_DIR__REL_HOME_ACT),
)
