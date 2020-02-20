"""
FilesCondition - a set of file names, each with an optional `FileMatcher`.
"""
from pathlib import PurePosixPath
from typing import Sequence, Optional, Tuple, Mapping, List

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.details_structured import WithDetailsDescription
from exactly_lib.type_system.logic.file_matcher import FileMatcherAdv, GenericFileMatcherSdv, \
    FileMatcherDdv, FileMatcher
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.functional import map_optional
from exactly_lib.util.symbol_table import SymbolTable


class FilesCondition(WithDetailsDescription):
    def __init__(self, files: Mapping[PurePosixPath, Optional[FileMatcher]]):
        self._files = files

    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

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
        self._files = files
        self._validator = self._validator_validator_of_files()

    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesConditionAdv:
        path_2_matchers = self._combine_identical_file_names(tcds)
        path_2_mb_matcher = {
            path: self._all_matcher(matchers)
            for path, matchers in path_2_matchers.items()
        }
        return FilesConditionAdv(path_2_mb_matcher)

    def _combine_identical_file_names(self, tcds: Tcds) -> Mapping[PurePosixPath, List[FileMatcherAdv]]:
        def value_of_any_dependency(ddv: FileMatcherDdv) -> FileMatcherAdv:
            return ddv.value_of_any_dependency(tcds)

        ret_val = {}
        for file_name, mb_matcher_ddv in self._files:
            path = PurePosixPath(file_name.value_when_no_dir_dependencies())
            mb_matcher_adv = map_optional(value_of_any_dependency, mb_matcher_ddv)
            matchers = ret_val.setdefault(path, [])
            if mb_matcher_adv is not None:
                matchers.append(mb_matcher_adv)

        return ret_val

    @staticmethod
    def _all_matcher(matchers: List[FileMatcherAdv]) -> Optional[FileMatcherAdv]:
        if not matchers:
            return None
        if len(matchers) == 1:
            return matchers[0]
        return combinator_matchers.conjunction_adv(matchers)

    def _validator_validator_of_files(self) -> DdvValidator:
        validators = []

        for file_name, mb_matcher in self._files:
            validators.append(_IsRelativePosixPath(file_name.value_when_no_dir_dependencies()))
            if mb_matcher is not None:
                validators.append(mb_matcher.validator)

        return ddv_validators.all_of(validators)


class FilesConditionSdv(LogicWithDescriberSdv[FilesCondition]):
    def __init__(self, files: Sequence[Tuple[StringSdv, Optional[GenericFileMatcherSdv]]]):
        self._files = files
        self._references = []
        for file_name, mb_matcher in files:
            self._references += file_name.references
            if mb_matcher:
                self._references += mb_matcher.references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:

        def resolve_matcher(x: GenericFileMatcherSdv) -> FileMatcherDdv:
            return x.resolve(symbols)

        def resolve_entry(file_name: StringSdv, matcher: Optional[GenericFileMatcherSdv]
                          ) -> Tuple[StringDdv, Optional[FileMatcherDdv]]:
            return file_name.resolve(symbols), map_optional(resolve_matcher, matcher)

        return FilesConditionDdv([
            resolve_entry(fn, mb_matcher)
            for fn, mb_matcher in self._files
        ])


class _IsRelativePosixPath(DdvValidator):
    def __init__(self, path_str: str):
        self.path_str = path_str

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        if self.path_str == '':
            return text_docs.single_line(_EMPTY_FILE_NAME)

        path = PurePosixPath(self.path_str)
        if path.is_absolute():
            return text_docs.single_line(
                strings.FormatMap(
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
_EMPTY_FILE_NAME = strings.FormatMap('A {FILE_NAME} must not be the empty string',
                                     _FORMAT_MAP)
