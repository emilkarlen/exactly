from pathlib import PurePosixPath
from typing import Sequence, Optional, TypeVar, Generic

from exactly_lib.common.report_rendering import header_blocks
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.sdv_structure import SymbolReference, TypesSymbolDependentValue, \
    references_from_objects_with_symbol_references
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv, FilesSourceAdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.description.details_structured import WithDetailsDescription
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable
from .. import syntax
from ..file_maker import FileMakerAdv, FileMakerDdv, FileMakerSdv, FileMaker

FILE_NAME_STRING_REFERENCES_RESTRICTION = reference_restrictions.is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'A {file_name} must be defined in terms of {string_type}.',
            {
                'file_name': syntax.FILE_NAME.name,
                'string_type': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name
            },
        )
    )
)


class FileSpecification(WithDetailsDescription):
    def __init__(self,
                 file_name: str,
                 file_maker: FileMaker,
                 ):
        self.name = file_name
        self.maker = file_maker

    @property
    def describer(self) -> DetailsRenderer:
        return self.maker.describer(self.name)


class FileSpecificationAdv(ApplicationEnvironmentDependentValue[FileSpecification]):
    def __init__(self,
                 name: str,
                 maker: FileMakerAdv,
                 ):
        self._name = name
        self._maker = maker

    def primitive(self, environment: ApplicationEnvironment) -> FileSpecification:
        return FileSpecification(self._name,
                                 self._maker.primitive(environment))


class FileSpecificationDdv(WithDetailsDescription):
    def __init__(self,
                 name: str,
                 maker: FileMakerDdv,
                 ):
        self.name = name
        self.maker = maker
        self._validator = ddv_validators.all_of([
            _IsValidPosixPath(name),
            self.maker.validator,
        ])

    @property
    def describer(self) -> DetailsRenderer:
        return self.maker.describer(self.name)

    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> FileSpecificationAdv:
        return FileSpecificationAdv(
            self.name,
            self.maker.value_of_any_dependency(tcds),
        )


class FileSpecificationSdv(TypesSymbolDependentValue[FileSpecificationDdv]):
    def __init__(self,
                 name: StringSdv,
                 maker: FileMakerSdv,
                 ):
        self._name = name
        self._maker = maker

    @property
    def references(self) -> Sequence[SymbolReference]:
        return tuple(self._name.references) + tuple(self._maker.references)

    def resolve(self, symbols: SymbolTable) -> FileSpecificationDdv:
        return FileSpecificationDdv(
            self._name.resolve(symbols).value_when_no_dir_dependencies(),
            self._maker.resolve(symbols),
        )


class Primitive(FilesSource):
    def __init__(self, files: Sequence[FileSpecification]):
        self._files = files
        self._describer = _Describer(self._files)

    @property
    def describer(self) -> DetailsRenderer:
        return self._describer

    def populate(self, directory: DescribedPath):
        for file in self._files:
            file.maker.make(_child_dp(directory, PurePosixPath(file.name)))


class _Adv(FilesSourceAdv):
    def __init__(self, files: Sequence[FileSpecificationAdv]):
        self._files = files

    def primitive(self, environment: ApplicationEnvironment) -> FilesSource:
        return Primitive([
            file.primitive(environment)
            for file in self._files
        ])


class _Ddv(FilesSourceDdv):
    def __init__(self, files: Sequence[FileSpecificationDdv]):
        self._files = files
        validators = [
            file.validator()
            for file in files
        ]
        self._validator = ddv_validators.all_of(validators)

    @property
    def describer(self) -> DetailsRenderer:
        return _Describer(self._files)

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> FilesSourceAdv:
        return _Adv([
            file.value_of_any_dependency(tcds)
            for file in self._files
        ])


class Sdv(FilesSourceSdv):
    def __init__(self, files: Sequence[FileSpecificationSdv]):
        self._files = files
        self._references = tuple(references_from_objects_with_symbol_references(files))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesSourceDdv:
        return _Ddv([
            file_spec.resolve(symbols)
            for file_spec in self._files
        ])


class _IsValidPosixPath(DdvValidator):

    def __init__(self, path: str):
        self.path_str = path

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        path_str = self.path_str
        if path_str == '':
            return text_docs.single_line(_ERR__FILE_NAME__EMPTY)

        for path_separator in _PATH_SEPARATORS:
            if path_separator in path_str:
                return self._err_msg(path_str, _ERR__FILE_NAME__PATH_SEPARATOR_IN_FILE_NAME)

        path = PurePosixPath(path_str)
        if path.is_absolute():
            return self._err_msg(path_str, _ERR__FILE_NAME__ABSOLUTE)
        if '..' in path.parts:
            return self._err_msg(path_str, _ERR__FILE_NAME__RELATIVE_COMPONENTS)

        return None

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        return None

    @staticmethod
    def _err_msg(path: str,
                 header_tmpl: str) -> TextRenderer:
        header = str_constructor.FormatMap(header_tmpl, _FORMAT_MAP)
        return rend_comb.SingletonSequenceR(
            header_blocks.w_details(
                header,
                text_docs.minor_blocks_of_string_lines([path])
            )
        )


_PATH_SEPARATORS = (':', ';')


def _string_constant(s: str) -> str:
    return ''.join(('\'', s, '\''))


_PATH_SEPARATORS_LIST = ','.join([
    _string_constant(sep)
    for sep in _PATH_SEPARATORS
])

_FORMAT_MAP = {
    'FILE_NAME': syntax.FILE_NAME.name,
    'PATH_SEPARATORS': _PATH_SEPARATORS_LIST,
    'RELATIVE_COMPONENT': _string_constant('..'),
}

_ERR__FILE_NAME__EMPTY = str_constructor.FormatMap(
    '{FILE_NAME} must not be the empty string',
    _FORMAT_MAP,
)

_ERR__FILE_NAME__PATH_SEPARATOR_IN_FILE_NAME = '{FILE_NAME} must not contain path separators ({PATH_SEPARATORS})'

_ERR__FILE_NAME__ABSOLUTE = '{FILE_NAME} must not be absolute'
_ERR__FILE_NAME__RELATIVE_COMPONENTS = '{FILE_NAME} must not contain relative components ({RELATIVE_COMPONENT}):'


def _child_dp(root: DescribedPath, relative_path: PurePosixPath) -> DescribedPath:
    ret_val = root
    for component in relative_path.parts:
        ret_val = ret_val.child(component)
    return ret_val


FILE_SPEC = TypeVar('FILE_SPEC', bound=WithDetailsDescription)


class _Describer(Generic[FILE_SPEC], DetailsRenderer):
    EMPTY_RENDERER = details.String(' '.join((syntax.FILE_LIST_BEGIN, syntax.FILE_LIST_END)))
    BEGIN_BRACE_RENDERER = details.String(syntax.FILE_LIST_BEGIN)
    END_BRACE_RENDERER = details.String(syntax.FILE_LIST_END)

    def __init__(self, files: Sequence[FILE_SPEC]):
        self._files = files

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _renderer(self) -> DetailsRenderer:
        return (
            self.EMPTY_RENDERER
            if len(self._files) == 0
            else
            self._renderer_of_non_empty()
        )

    def _renderer_of_non_empty(self) -> DetailsRenderer:
        entries_renderer = details.SequenceRenderer([
            file_spec.describer
            for file_spec in self._files
        ])

        return details.SequenceRenderer([
            self.BEGIN_BRACE_RENDERER,
            details.IndentedRenderer(entries_renderer),
            self.END_BRACE_RENDERER,
        ])
