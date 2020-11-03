import os.path
import pathlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from exactly_lib.definitions import path
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelOptionType, DirectoryStructurePartition, \
    SpecificPathRelativity
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path import path_part_ddvs
from exactly_lib.type_val_deps.types.path.impl import primitive_str_renderers, value_str_renderers, \
    describer_from_str as _from_str, described_w_handler
from exactly_lib.type_val_deps.types.path.impl.described_w_handler import PathDescriberHandlerForDdv, \
    PathDescriberHandlerForPrimitive
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv, DescribedPath
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_prims.path_describer import PathDescriberForDdv, PathDescriberForPrimitive
from exactly_lib.util.render.renderer import Renderer


class PathManipulationFunctionalityForFixedDdv(PathDescriberForDdv, ABC):
    """
    A SDV + value that has been fixed by symbols and TCDS.

    Used by objects representing a primitive value.
    Acts as a helper for functionality of the path manipulations
    supported by primitive value handlers
    (child, parent).
    """

    def __init__(self, ddv: PathDdv):
        self._ddv = ddv

    @property
    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._ddv.resolving_dependency()

    @abstractmethod
    def child(self, child_path_component: str) -> 'PathManipulationFunctionalityForFixedDdv':
        pass

    @abstractmethod
    def parent(self) -> 'PathManipulationFunctionalityForFixedDdv':
        pass

    def _child_value(self, child_path_component: str) -> PathDdv:
        return path_ddvs.stacked(
            self._ddv,
            path_part_ddvs.PathPartDdvAsFixedPath(child_path_component),
        )

    def _parent_value(self) -> PathDdv:
        return _ParentPathDdv(self._ddv)


class PathDescriberHandlerForDdvWithDdv(PathDescriberHandlerForDdv):
    def __init__(self, path_ddv: PathDdv):
        self._path_ddv = path_ddv
        self._relativity_type = path_ddv.relativity().relativity_type

    @property
    def describer(self) -> PathDescriberForDdv:
        return _from_str.PathDescriberForDdvFromStr(
            self._value_renderer_before_fixation(),
            self._resolving_dependency,
        )

    def value_when_no_dir_dependencies(self, primitive: Path) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_ddv,
            ),
        )

    def value_pre_sds(self, primitive: Path, hds: HomeDs) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_ddv,
            ),
        )

    def value_post_sds__wo_hds(self, primitive: Path,
                               sds: SandboxDs) -> PathDescriberHandlerForPrimitive:
        return self.value_post_sds(primitive, TestCaseDs(_DUMMY_HDS, sds))

    def value_post_sds(self, primitive: Path, tcds: TestCaseDs) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            self._fixation(tcds),
        )

    def value_of_any_dependency(self, primitive: Path, tcds: TestCaseDs) -> PathDescriberHandlerForPrimitive:
        return PathDescriberHandlerForPrimitiveWithPrimitive(
            primitive,
            self._fixation(tcds),
        )

    def _resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._path_ddv.resolving_dependency()

    def _fixation(self, tcds: TestCaseDs) -> PathManipulationFunctionalityForFixedDdv:
        if self._relativity_type is RelOptionType.REL_CWD:
            return PathManipulationFunctionalityForFixedValueForRelCwd(
                self._path_ddv,
                tcds,
                Path().cwd(),
            )
        else:
            return PathManipulationFunctionalityForFixedValueForNotRelCwd(
                self._path_ddv,
            )

    def _value_renderer_before_fixation(self) -> Renderer[str]:
        relativity_type = self._relativity_type

        if relativity_type is RelOptionType.REL_CWD:
            return value_str_renderers.PathValueRelUnknownCwd(self._path_ddv)
        elif relativity_type is None:
            return value_str_renderers.PathValuePlainAbsolute(self._path_ddv)
        else:
            return value_str_renderers.PathValueRelTcdsDir(self._path_ddv)


class PathManipulationFunctionalityForFixedValueForNotRelCwd(PathManipulationFunctionalityForFixedDdv):
    def __init__(self, ddv: PathDdv):
        super().__init__(ddv)

    @property
    def value(self) -> Renderer[str]:
        value = self._ddv
        relativity_type = value.relativity().relativity_type
        return (
            value_str_renderers.PathValuePlainAbsolute(value)
            if relativity_type is None
            else
            value_str_renderers.PathValueRelTcdsDir(value)
        )

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedDdv:
        return PathManipulationFunctionalityForFixedValueForNotRelCwd(
            self._child_value(child_path_component),
        )

    def parent(self) -> PathManipulationFunctionalityForFixedDdv:
        return PathManipulationFunctionalityForFixedValueForNotRelCwd(
            self._parent_value(),
        )


class PathManipulationFunctionalityForFixedValueForRelCwd(PathManipulationFunctionalityForFixedDdv):
    def __init__(self,
                 ddv: PathDdv,
                 tcds: TestCaseDs,
                 cwd: Optional[Path],
                 ):
        super().__init__(ddv)
        self._tcds = tcds
        self._cwd = cwd

    @property
    def value(self) -> Renderer[str]:
        return (
            value_str_renderers.PathValueRelUnknownCwd(self._ddv)
            if self._cwd is None
            else
            value_str_renderers.PathValueRelCwd(self._ddv, self._cwd, self._tcds)
        )

    def child(self, child_path_component: str) -> PathManipulationFunctionalityForFixedDdv:
        return PathManipulationFunctionalityForFixedValueForRelCwd(
            self._child_value(child_path_component),
            self._tcds,
            self._cwd,
        )

    def parent(self) -> PathManipulationFunctionalityForFixedDdv:
        return PathManipulationFunctionalityForFixedValueForRelCwd(
            self._parent_value(),
            self._tcds,
            self._cwd,
        )


class PathDescriberHandlerForPrimitiveWithPrimitive(PathDescriberHandlerForPrimitive):
    def __init__(self,
                 primitive: Path,
                 fixed_value: PathManipulationFunctionalityForFixedDdv,
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


class _ParentPathDdv(PathDdv):
    def __init__(self, original: PathDdv):
        self._original = original
        self._value = None

    def path_suffix(self) -> PathPartDdv:
        return self._get_ddv().path_suffix()

    def path_suffix_str(self) -> str:
        return self._get_ddv().path_suffix_str()

    def path_suffix_path(self) -> pathlib.Path:
        return self._get_ddv().path_suffix_path()

    def relativity(self) -> SpecificPathRelativity:
        return self._get_ddv().relativity()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        return self._get_ddv().value_when_no_dir_dependencies()

    def value_pre_sds(self, hds: HomeDs) -> pathlib.Path:
        return self._get_ddv().value_pre_sds(hds)

    def value_post_sds(self, sds: SandboxDs) -> pathlib.Path:
        return self._get_ddv().value_post_sds(sds)

    def describer(self) -> PathDescriberForDdv:
        return self._describer_handler().describer

    def value_when_no_dir_dependencies__d(self) -> DescribedPath:
        primitive = self.value_when_no_dir_dependencies()
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_when_no_dir_dependencies(primitive),
        )

    def value_pre_sds__d(self, hds: HomeDs) -> DescribedPath:
        primitive = self.value_pre_sds(hds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_pre_sds(primitive, hds),
        )

    def value_post_sds__d(self, sds: SandboxDs) -> DescribedPath:
        primitive = self.value_post_sds(sds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_post_sds__wo_hds(primitive, sds),
        )

    def value_of_any_dependency__d(self, tcds: TestCaseDs) -> DescribedPath:
        primitive = self.value_of_any_dependency(tcds)
        return described_w_handler.DescribedPathWHandler(
            primitive,
            self._describer_handler().value_of_any_dependency(primitive, tcds),
        )

    def _describer_handler(self) -> PathDescriberHandlerForDdv:
        return PathDescriberHandlerForDdvWithDdv(self)

    def _get_ddv(self) -> PathDdv:
        if self._value is None:
            original = self._original
            path_suffix = self._parent_path_suffix(original.path_suffix().value())
            relativity = original.relativity()
            self._value = (
                path_ddvs.absolute_part(path_suffix)
                if relativity.is_absolute
                else
                path_ddvs.of_rel_option(relativity.relativity_type,
                                        path_suffix)
            )

        return self._value

    @staticmethod
    def _parent_path_suffix(path_suffix: str) -> PathPartDdv:
        if path_suffix == '':
            return path_ddvs.constant_path_part('..')

        (head, tail) = os.path.split(path_suffix)

        return path_ddvs.constant_path_part(head)


_DUMMY_HDS = HomeDs(
    pathlib.Path(path.EXACTLY_DIR__REL_HDS_CASE),
    pathlib.Path(path.EXACTLY_DIR__REL_HDS_ACT),
)
