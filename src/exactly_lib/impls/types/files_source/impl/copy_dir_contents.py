import pathlib
from typing import Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls import file_properties
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.path import path_check
from exactly_lib.impls.types.path import path_rendering
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv, FilesSourceAdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MinorBlock
from exactly_lib.util.symbol_table import SymbolTable
from .. import syntax


class CopyDirContentsSdv(FilesSourceSdv):
    def __init__(self, src_dir: PathSdv):
        self._src_dir = src_dir

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._src_dir.references

    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        return _CopyDirContentsDdv(self._src_dir.resolve(symbols))


class _CopyDirContents(FilesSource):
    def __init__(self,
                 src_dir: DescribedPath,
                 environment: ApplicationEnvironment,
                 ):
        self._src_dir = src_dir
        self._environment = environment

    @property
    def describer(self) -> DetailsRenderer:
        return _description_of(
            custom_details.PathDdvAndPrimitiveIfRelHomeAsIndentedDetailsRenderer(
                self._src_dir.describer
            )
        )

    def populate(self, directory: DescribedPath):
        for src_path in self._src_dir.primitive.iterdir():
            self._copy_path(src_path.name, directory)

    def _copy_path(self,
                   src_file_name: str,
                   dst_dir_path: DescribedPath):
        src_file_path = self._src_dir.child(src_file_name)
        dst_path = dst_dir_path.primitive / src_file_name
        try:
            dst_path.lstat()
            self._raise_file_name_clash(src_file_name, dst_dir_path)
        except FileNotFoundError:
            self._copy_file(src_file_path.primitive, dst_path)

    def _copy_file(self, src_file: pathlib.Path, dst_file: pathlib.Path):
        if src_file.is_dir():
            self._environment.os_services.copy_tree__preserve_as_much_as_possible(
                str(src_file),
                str(dst_file),
            )
        else:
            self._environment.os_services.copy_file(
                src_file,
                dst_file,
            )

    def _raise_file_name_clash(self,
                               src_file_name: str,
                               dst_dir_path: DescribedPath,
                               ):
        rendering = _FileNameClashRendering(self._src_dir, dst_dir_path, src_file_name)
        err_msg_renderer = rendering.renderer()
        raise HardErrorException(err_msg_renderer)


class _CopyDirContentsAdv(FilesSourceAdv):
    def __init__(self, src_dir: DescribedPath):
        self._src_dir = src_dir

    def primitive(self, environment: ApplicationEnvironment) -> FilesSource:
        return _CopyDirContents(self._src_dir, environment)


class _CopyDirContentsDdv(FilesSourceDdv):
    def __init__(self, src_dir: PathDdv):
        self._src_dir = src_dir
        self._validator = path_check.PathCheckDdvValidator(
            path_check.PathCheckDdv(
                src_dir,
                file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                              follow_symlinks=True)
            )
        )

    @property
    def describer(self) -> DetailsRenderer:
        return _description_of(
            custom_details.PathDdvDetailsRenderer(self._src_dir.describer())
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[FilesSource]:
        return _CopyDirContentsAdv(self._src_dir.value_of_any_dependency__d(tcds))


class _FileNameClashRendering:
    _SRC_PATH_HEADER = 'Path in ' + instruction_arguments.SOURCE_PATH_ARGUMENT.name
    _DST_PATH_HEADER = 'exists in ' + instruction_arguments.DESTINATION_PATH_ARGUMENT.name

    def __init__(self,
                 src_dir: DescribedPath,
                 dst_dir: DescribedPath,
                 file_name: str,
                 ):
        self._src_dir = src_dir
        self._dst_dir = dst_dir
        self._file_name = file_name

    def renderer(self) -> TextRenderer:
        return rend_comb.SingletonSequenceR(
            comp_rend.MajorBlockR(self._minor_blocks_renderer())
        )

    def _minor_blocks_renderer(self) -> SequenceRenderer[MinorBlock]:
        return rend_comb.ConcatenationR([
            path_rendering.HeaderAndPathMinorBlocks.of_string_header(
                self._SRC_PATH_HEADER,
                self._src_dir.child(self._file_name).describer,
            ),
            path_rendering.HeaderAndPathMinorBlocks.of_string_header(
                self._DST_PATH_HEADER,
                self._dst_dir.child(self._file_name).describer,
            ),
        ])


_DESCRIPTION_HEADER = ' '.join((syntax.COPY_CONTENTS_OF_EXISTING_DIR,
                                syntax_elements.PATH_SYNTAX_ELEMENT.singular_name))


def _description_of(path: DetailsRenderer) -> DetailsRenderer:
    return details.HeaderAndValue(_DESCRIPTION_HEADER, path)
