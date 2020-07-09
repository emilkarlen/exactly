"""
FilesCondition - a set of file names, each with an optional `FileMatcher`.
"""
from abc import ABC, abstractmethod
from pathlib import PurePosixPath
from typing import Sequence, Optional, Tuple, Mapping, List, TypeVar, Generic

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.details_structured import WithDetailsDescription
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.file_matcher import FileMatcherAdv, FileMatcherDdv, FileMatcher
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.functional import map_optional
from exactly_lib.util.render import strings as string_rendering
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable


class FilesCondition(WithDetailsDescription):
    def __init__(self, files: Mapping[PurePosixPath, Optional[FileMatcher]]):
        self._files = files
        self._describer = _Describer(files)

    @property
    def describer(self) -> DetailsRenderer:
        return self._describer

    @property
    def files(self) -> Mapping[PurePosixPath, Optional[FileMatcher]]:
        return self._files


class FilesConditionAdv(ApplicationEnvironmentDependentValue[FilesCondition]):
    def __init__(self, files: Mapping[PurePosixPath, Optional[FileMatcherAdv]]):
        self._files = files

    def primitive(self, environment: ApplicationEnvironment) -> FilesCondition:
        def resolve_matcher(adv: FileMatcherAdv) -> FileMatcher:
            return adv.primitive(environment)

        return FilesCondition({
            path: map_optional(resolve_matcher, mb_matcher)
            for path, mb_matcher in self._files.items()
        })


class FilesConditionDdv(LogicWithDetailsDescriptionDdv[FilesCondition]):
    def __init__(self, files: Sequence[Tuple[StringDdv, Optional[FileMatcherDdv]]]):
        helper = _DdvHelper(files)
        self._files = helper.files_as_map()
        self._validator = helper.validator_validator_of_files()
        self._describer = _Describer(self._files)

    @property
    def describer(self) -> DetailsRenderer:
        return self._describer

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesConditionAdv:
        def val_of_any_dep(matcher: FileMatcherDdv) -> FileMatcherAdv:
            return matcher.value_of_any_dependency(tcds)

        return FilesConditionAdv({
            path: map_optional(val_of_any_dep, mb_matcher)
            for path, mb_matcher in self._files.items()
        })


class FilesConditionSdv(LogicWithDetailsDescriptionSdv[FilesCondition], ABC):
    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:
        pass


class _IsRelativePosixPath(DdvValidator):
    def __init__(self, path_str: str):
        self.path_str = path_str

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        if self.path_str == '':
            return text_docs.single_line(_EMPTY_FILE_NAME)

        path = PurePosixPath(self.path_str)
        if path.is_absolute():
            return text_docs.single_line(
                str_constructor.FormatMap(
                    'A {FILE_NAME} must not be absolute: {path}',
                    {
                        'FILE_NAME': syntax.FILE_NAME,
                        'path': str(path),
                    }
                )
            )
        return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        return None


_FORMAT_MAP = {
    'FILE_NAME': syntax.FILE_NAME,
}
_EMPTY_FILE_NAME = str_constructor.FormatMap(
    'A {FILE_NAME} must not be the empty string',
    _FORMAT_MAP,
)

TSD = TypeVar('TSD', bound=WithTreeStructureDescription)


class _Describer(Generic[TSD], DetailsRenderer):
    def __init__(self, files: Mapping[PurePosixPath, Optional[TSD]]):
        self._files = files

    def render(self) -> Sequence[Detail]:
        return self._renderer().render()

    def _entries(self) -> Sequence[Tuple[Renderer[str], Optional[TSD]]]:
        files = self._files
        return [
            (string_rendering.of_to_string_object(fn), files[fn])
            for fn in sorted(files.keys())
        ]

    def _renderer(self) -> DetailsRenderer:
        entries = self._entries()

        if len(entries) == 0:
            return _EMPTY_RENDERER
        else:
            return self._renderer_of_non_empty(entries)

    def _renderer_of_non_empty(self, entries: Sequence[Tuple[Renderer[str], Optional[TSD]]]
                               ) -> DetailsRenderer:
        entries_renderer = details.SequenceRenderer([
            self._file(fn, mb_matcher)
            for fn, mb_matcher in entries
        ])

        return details.SequenceRenderer([
            _BEGIN_BRACE_RENDERER,
            details.IndentedRenderer(entries_renderer),
            _END_BRACE_RENDERER,
        ])

    @staticmethod
    def _file(path: Renderer[str],
              mb_matcher: Optional[TSD],
              ) -> DetailsRenderer:
        path_string = path.render()
        return (
            details.String(path_string)
            if mb_matcher is None
            else
            details.HeaderAndValue(
                path_string,
                custom_details.WithTreeStructure(mb_matcher)
            )
        )


class _DdvHelper:
    def __init__(self, files: Sequence[Tuple[StringDdv, Optional[FileMatcherDdv]]]):
        self._files = files

    def files_as_map(self) -> Mapping[PurePosixPath, Optional[FileMatcherDdv]]:
        path_2_matchers = self._group_identical_file_names()
        return {
            path: self._all_matcher(matchers)
            for path, matchers in path_2_matchers.items()
        }

    def _group_identical_file_names(self) -> Mapping[PurePosixPath, List[FileMatcherDdv]]:
        ret_val = {}
        for file_name, mb_matcher_ddv in self._files:
            path = PurePosixPath(file_name.value_when_no_dir_dependencies())
            matchers = ret_val.setdefault(path, [])
            if mb_matcher_ddv is not None:
                matchers.append(mb_matcher_ddv)

        return ret_val

    @staticmethod
    def _all_matcher(matchers: List[FileMatcherDdv]) -> Optional[FileMatcherDdv]:
        if not matchers:
            return None
        if len(matchers) == 1:
            return matchers[0]
        return combinator_matchers.ConjunctionDdv(matchers)

    def validator_validator_of_files(self) -> DdvValidator:
        validators = []

        for file_name, mb_matcher in self._files:
            validators.append(_IsRelativePosixPath(file_name.value_when_no_dir_dependencies()))
            if mb_matcher is not None:
                validators.append(mb_matcher.validator)

        return ddv_validators.all_of(validators)


_EMPTY_RENDERER = details.String(' '.join((syntax.BEGIN_BRACE, syntax.END_BRACE)))

_BEGIN_BRACE_RENDERER = details.String(syntax.BEGIN_BRACE)

_END_BRACE_RENDERER = details.String(syntax.END_BRACE)
