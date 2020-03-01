from abc import ABC
from pathlib import PurePosixPath, Path
from typing import Callable, Sequence, List, Optional, Mapping

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionAdv, FilesConditionDdv, \
    FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.matcher.impls import combinator_matchers
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, FilesMatcherAdv, \
    FilesMatcherDdv, GenericFilesMatcherSdv, FileModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherAdv, MatcherDdv, \
    MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.symbol_table import SymbolTable


def equals_sdv(files_condition: FilesConditionSdv) -> GenericFilesMatcherSdv:
    return _MatcherSdv(_EQUALS_CONFIG, files_condition)


def contains_sdv(files_condition: FilesConditionSdv) -> GenericFilesMatcherSdv:
    return _MatcherSdv(_CONTAINS_CONFIG, files_condition)


class _Conf:
    def __init__(self,
                 name: str,
                 make_matcher: Callable[[str, FilesCondition], FilesMatcher],
                 ):
        self.name = name
        self.make_matcher = make_matcher


class _MatcherBase(MatcherWTraceAndNegation[FilesMatcherModel], ABC):
    def __init__(self,
                 name: str,
                 files_condition: FilesCondition,
                 ):
        self._structure_name = ' '.join((name, syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name))
        self._files_condition = files_condition
        self._structure = self.new_structure_tree(name, files_condition.describer)

    @staticmethod
    def new_structure_tree(name: str, files_condition: DetailsRenderer) -> StructureRenderer:
        structure_header = ' '.join((name, syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT.singular_name))
        return renderers.header_and_detail(structure_header, files_condition)

    @property
    def name(self) -> str:
        return self._structure_name

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def negation(self) -> FilesMatcher:
        return combinator_matchers.Negation(self)


class _Equals(_MatcherBase):
    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return _EqualsApplier(self._structure_name,
                              self._files_condition,
                              model).apply()


class _Contains(_MatcherBase):
    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        return _ContainsApplier(self._structure_name,
                                self._files_condition,
                                model).apply()


class _NameMatch:
    def __init__(self,
                 fc_path: PurePosixPath,
                 fc_matcher: Optional[FilesMatcher],
                 match_from_model: FileModel,
                 ):
        self.fc_path = fc_path
        self.fc_matcher = fc_matcher
        self.match_from_model = match_from_model


class _EqualsApplier:
    def __init__(self,
                 name: str,
                 files_condition: FilesCondition,
                 model: FilesMatcherModel,
                 ):
        self.name = name
        self.model = model
        self.files_condition = files_condition

    def apply(self) -> MatchingResult:
        return self._start_w_num_files_check()

    def _start_w_num_files_check(self) -> MatchingResult:
        expected_num_files = len(self.files_condition.files.keys())

        actual_files = self._try_get_num_files(expected_num_files + 1)

        if len(actual_files) != expected_num_files:
            return self._report_unexpected_num_files(actual_files)

        return self._continue_w_file_name_check(actual_files)

    def _continue_w_file_name_check(self, actual: List[FileModel]) -> MatchingResult:
        """
        :param actual: Contains expected number of files
        """
        files = self.files_condition.files
        name_matches = []

        for actual_file in actual:
            actual_as_pure_posix = PurePosixPath(actual_file.relative_to_root_dir)
            try:
                corresponding_file_matcher = files[actual_as_pure_posix]
                name_matches.append(_NameMatch(actual_as_pure_posix,
                                               corresponding_file_matcher,
                                               actual_file))
            except KeyError:
                return MatchingResult(False,
                                      _UnexpectedFile(actual_file, self))

        return self._continue_w_file_matcher_check(name_matches)

    def _continue_w_file_matcher_check(self, files: List[_NameMatch]) -> MatchingResult:
        for name_match in files:
            if name_match.fc_matcher is not None:
                file_model = name_match.match_from_model.as_file_matcher_model()
                matching_result = name_match.fc_matcher.matches_w_trace(file_model)
                if not matching_result.value:
                    return MatchingResult(False, _NonMatchingFileMatcher(name_match,
                                                                         matching_result,
                                                                         self))

        return MatchingResult(True, renderers.header_only__w_value(self.name, True))

    def _try_get_num_files(self, num_files: int) -> List[FileModel]:
        """
        :param num_files: >= 1
        """
        ret_val = []
        num_fetched = 0
        for x in self.model.files():
            ret_val.append(x)
            num_fetched += 1
            if num_fetched == num_files:
                break

        return ret_val

    def _report_unexpected_num_files(self, fetched: List[FileModel]) -> MatchingResult:
        return MatchingResult(False, _UnexpectedNumFiles(fetched, self))


class _ContainsApplier:
    def __init__(self,
                 name: str,
                 files_condition: FilesCondition,
                 model: FilesMatcherModel,
                 ):
        self.name = name
        self.model = model
        self.files_condition = files_condition

    def apply(self) -> MatchingResult:
        if len(self.files_condition.files) == 0:
            return MatchingResult(True,
                                  renderers.header_only__w_value(self.name, True))

        expected_files = {
            Path(posix_path): mb_fm
            for posix_path, mb_fm in self.files_condition.files.items()
        }

        for actual_file in self.model.files():
            relative_file_name = actual_file.relative_to_root_dir
            if relative_file_name in expected_files:
                mb_matcher = expected_files[relative_file_name]
                if mb_matcher is not None:
                    matching_result = mb_matcher.matches_w_trace(actual_file.as_file_matcher_model())
                    if not matching_result.value:
                        return MatchingResult(False,
                                              _ContainsNonMatchingMatcher(self.name,
                                                                          actual_file,
                                                                          matching_result))

                del expected_files[relative_file_name]

                if len(expected_files) == 0:
                    return MatchingResult(True,
                                          renderers.header_only__w_value(self.name, True))

        return MatchingResult(False,
                              _ContainsFilesNotFound(self.name, expected_files))


class _ContainsNonMatchingMatcher(NodeRenderer[bool]):
    def __init__(self,
                 name: str,
                 non_matching_file: FileModel,
                 match_trace: MatchingResult,
                 ):
        self._name = name
        self._non_matching_file = non_matching_file
        self._match_trace = match_trace

    def render(self) -> Node[bool]:
        return Node.empty(self._name, False)


class _ContainsFilesNotFound(NodeRenderer[bool]):
    def __init__(self,
                 name: str,
                 files_not_found: Mapping[Path, Optional[FileModel]],
                 ):
        self._name = name
        self._files_not_found = files_not_found

    def render(self) -> Node[bool]:
        return Node.empty(self._name, False)


class _UnexpectedNumFiles(NodeRenderer[bool]):
    def __init__(self,
                 fetch_of_expected_plus_1: List[FileModel],
                 applier: _EqualsApplier,
                 ):
        self._fetch_of_expected_plus_1 = fetch_of_expected_plus_1
        self._applier = applier

    def render(self) -> Node[bool]:
        return Node.empty(self._applier.name, False)


class _UnexpectedFile(NodeRenderer[bool]):
    def __init__(self,
                 unexpected_file: FileModel,
                 applier: _EqualsApplier,
                 ):
        self._unexpected_file = unexpected_file
        self._applier = applier

    def render(self) -> Node[bool]:
        return Node.empty(self._applier.name, False)


class _NonMatchingFileMatcher(NodeRenderer[bool]):
    def __init__(self,
                 non_match: _NameMatch,
                 non_match_result: MatchingResult,
                 applier: _EqualsApplier,
                 ):
        self._non_match = non_match
        self._non_match_result = non_match_result
        self._applier = applier

    def render(self) -> Node[bool]:
        return Node.empty(self._applier.name, False)


class _MatcherAdv(MatcherAdv[FilesMatcherModel]):
    def __init__(self,
                 conf: _Conf,
                 files_condition: FilesConditionAdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    def primitive(self, environment: ApplicationEnvironment) -> FilesMatcher:
        return self._conf.make_matcher(self._conf.name,
                                       self._files_condition.primitive(environment))


class _MatcherDdv(MatcherDdv[FilesMatcherModel]):
    def __init__(self,
                 conf: _Conf,
                 files_condition: FilesConditionDdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    def structure(self) -> StructureRenderer:
        return _MatcherBase.new_structure_tree(self._conf.name,
                                               self._files_condition.describer)

    @property
    def validator(self) -> DdvValidator:
        return self._files_condition.validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherAdv:
        return _MatcherAdv(self._conf,
                           self._files_condition.value_of_any_dependency(tcds))


class _MatcherSdv(MatcherSdv[FilesMatcherModel]):
    def __init__(self,
                 conf: _Conf,
                 files_condition: FilesConditionSdv,
                 ):
        self._conf = conf
        self._files_condition = files_condition

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._files_condition.references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _MatcherDdv(self._conf,
                           self._files_condition.resolve(symbols))


def _make_equals(name: str, files_condition: FilesCondition) -> FilesMatcher:
    return _Equals(name, files_condition)


def _make_contains(name: str, files_condition: FilesCondition) -> FilesMatcher:
    return _Contains(name, files_condition)


_EQUALS_CONFIG = _Conf(config.EQUALS_ARGUMENT,
                       _make_equals)

_CONTAINS_CONFIG = _Conf(config.CONTAINS_ARGUMENT,
                         _make_contains)
