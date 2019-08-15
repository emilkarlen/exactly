import pathlib

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForValue, PathDescriberForPrimitive, \
    PathDescriberForResolver
from exactly_lib.test_case_utils.err_msg2.path_impl import path_describer_from_str as _from_str
from exactly_lib.test_case_utils.err_msg2.path_impl import path_primitive_str_renderers
from exactly_lib.test_case_utils.err_msg2.path_impl import path_value_str_renderers
from exactly_lib.test_case_utils.err_msg2.path_impl.described_path_w_handler import PathDescriberHandlerForValue, \
    PathDescriberHandlerForResolver
from exactly_lib.test_case_utils.err_msg2.path_impl.path_resolver_str_renderers import PathResolverShouldNotBeUsed
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.symbol_table import SymbolTable


class PathDescriberHandlerForResolverWStrRenderer(PathDescriberHandlerForResolver):
    def __init__(self, path_resolver: FileRefResolver):
        self._path_resolver = path_resolver

    @property
    def describer(self) -> PathDescriberForResolver:
        return _from_str.PathDescriberForResolverFromStr(PathResolverShouldNotBeUsed(self._path_resolver))

    def resolve(self, symbols: SymbolTable) -> 'PathDescriberHandlerForValue':
        return PathDescriberHandlerForValueWStrRenderer(
            self._path_resolver.resolve(symbols),
            self.describer,
        )


class PathDescriberHandlerForValueWStrRenderer(PathDescriberHandlerForValue):
    def __init__(self,
                 path_value: FileRef,
                 resolver_describer: PathDescriberForResolver):
        self._cwd = None
        self._path_value = path_value
        self._relativity_type = path_value.relativity().relativity_type
        self._describer = _from_str.PathDescriberForValueFromStr(resolver_describer,
                                                                 self._value_renderer_for(path_value))
        self._resolver_describer = resolver_describer

    @property
    def describer(self) -> PathDescriberForValue:
        return self._describer

    def value_when_no_dir_dependencies(self) -> 'PathDescriberForPrimitive':
        return _from_str.PathDescriberForPrimitiveFromStr(
            self.describer,
            path_primitive_str_renderers.WithoutDependencies(self._path_value)
        )

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> 'PathDescriberForPrimitive':
        return _from_str.PathDescriberForPrimitiveFromStr(
            self.describer,
            path_primitive_str_renderers.DependentOnHds(self._path_value, hds)
        )

    def value_post_sds(self, tcds: HomeAndSds) -> 'PathDescriberForPrimitive':
        return _from_str.PathDescriberForPrimitiveFromStr(
            self._value_describer_post_sds(tcds),
            path_primitive_str_renderers.DependentOnSds(self._path_value, tcds.sds)
        )

    def value_of_any_dependency(self, tcds: HomeAndSds) -> 'PathDescriberForPrimitive':
        return _from_str.PathDescriberForPrimitiveFromStr(
            self._value_describer_post_sds(tcds),
            path_primitive_str_renderers.DependentOnAnything(self._path_value, tcds)
        )

    def _value_describer_post_sds(self, tcds: HomeAndSds) -> PathDescriberForValue:
        if self._relativity_type is RelOptionType.REL_CWD:
            return _from_str.PathDescriberForValueFromStr(
                self._resolver_describer,
                path_value_str_renderers.PathValueRelCwd(self._path_value,
                                                         self._cwd,
                                                         tcds)
            )
        else:
            return self.describer

    def _value_renderer_for(self, path_value: FileRef) -> Renderer[str]:
        relativity_type = self._relativity_type

        if relativity_type is RelOptionType.REL_CWD:
            self._cwd = pathlib.Path().cwd()
            return path_value_str_renderers.PathValueRelJustCwd(path_value,
                                                                self._cwd)

        if relativity_type is None:
            return path_value_str_renderers.PathValuePlainAbsolute(path_value)

        return path_value_str_renderers.PathValueRelTcdsDir(path_value)
