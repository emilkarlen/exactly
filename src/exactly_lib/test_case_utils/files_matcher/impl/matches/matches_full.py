from pathlib import PurePosixPath
from typing import List, Optional, Tuple, Iterable

from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv, FilesCondition
from exactly_lib.test_case_utils.files_matcher.impl.matches import common
from exactly_lib.type_system.logic.files_matcher import FilesMatcher, FilesMatcherSdv, \
    FileModel, FilesMatcherModel
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node


def sdv(files_condition: FilesConditionSdv) -> FilesMatcherSdv:
    return common.MatcherSdvWithApplier(_CONFIG, files_condition)


class _NameMatch:
    def __init__(self,
                 fc_path: PurePosixPath,
                 fc_matcher: Optional[FilesMatcher],
                 match_from_model: FileModel,
                 ):
        self.fc_path = fc_path
        self.fc_matcher = fc_matcher
        self.match_from_model = match_from_model


class _Applier(common.Applier):
    def __init__(self,
                 name: str,
                 files_condition: FilesCondition,
                 model: FilesMatcherModel,
                 ):
        super().__init__(name, files_condition, model)
        self.model_files_iter = model.files()

    def apply(self) -> MatchingResult:
        return self._start_w_num_files_check()

    def _start_w_num_files_check(self) -> MatchingResult:
        expected_num_files = len(self.files_condition.files.keys())

        actual_files = self._try_get_num_files(expected_num_files + 1)

        if len(actual_files) != expected_num_files:
            return MatchingResult(False,
                                  _RendererOfUnexpectedNumFiles(actual_files, self))

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
                                      _RendererOfFileWithUnexpectedName(actual_file, actual, self))

        return self._continue_w_file_matcher_check(name_matches)

    def _continue_w_file_matcher_check(self, files: List[_NameMatch]) -> MatchingResult:
        for name_match in files:
            if name_match.fc_matcher is not None:
                file_model = name_match.match_from_model.as_file_matcher_model()
                matching_result = name_match.fc_matcher.matches_w_trace(file_model)
                if not matching_result.value:
                    return MatchingResult(False,
                                          common.RendererOfNonMatchingFileMatcher(self.name,
                                                                                  name_match.fc_path,
                                                                                  matching_result))

        return self._result_true()

    def _try_get_num_files(self, num_files: int) -> List[FileModel]:
        """
        :param num_files: >= 1
        """
        ret_val = []
        num_fetched = 0
        for x in self.model_files_iter:
            ret_val.append(x)
            num_fetched += 1
            if num_fetched == num_files:
                break

        return ret_val


_CONFIG = common.Conf(common.MATCHES_FULL__STRUCTURE_NAME,
                      _Applier)


class _RendererOfUnexpectedNumFiles(NodeRenderer[bool]):
    def __init__(self,
                 fetch_of_expected_plus_1: List[FileModel],
                 applier: _Applier,
                 ):
        self._fetch_of_expected_plus_1 = fetch_of_expected_plus_1
        self._applier = applier

    def render(self) -> Node[bool]:
        get_explanation_and_actual = (
            self._too_few_files
            if len(self._fetch_of_expected_plus_1) < len(self._applier.files_condition.files.keys())
            else
            self._too_many_files
        )
        explanation, actual = get_explanation_and_actual()

        expected_and_actual = custom_details.ExpectedAndActual(
            self._expected(),
            actual,
            details.String(explanation),
        )

        return Node(self._applier.name,
                    False,
                    expected_and_actual.render(),
                    (),
                    )

    def _expected(self) -> DetailsRenderer:
        return _expected_file_names_renderer(self._applier.files_condition)

    def _too_few_files(self) -> Tuple[str, DetailsRenderer]:
        return (
            common.NUM_FILES_LESS,
            custom_details.string_list(self._consumed_file_names())
        )

    def _too_many_files(self) -> Tuple[str, DetailsRenderer]:
        file_list_elements = list(self._consumed_file_names())
        if self._model_has_more_files():
            file_list_elements.append(custom_details.HAS_MORE_DATA_MARKER)

        return (
            common.NUM_FILES_MORE,
            custom_details.string_list(file_list_elements)
        )

    def _consumed_file_names(self) -> Iterable[str]:
        return _files_in_model_list(self._fetch_of_expected_plus_1)

    def _model_has_more_files(self) -> bool:
        for _ in self._applier.model_files_iter:
            return True
        return False


class _RendererOfFileWithUnexpectedName(NodeRenderer[bool]):
    def __init__(self,
                 unexpected_file: FileModel,
                 actual: List[FileModel],
                 applier: _Applier,
                 ):
        self._unexpected_file = unexpected_file
        self._actual = actual
        self._applier = applier

    def render(self) -> Node[bool]:
        renderer = custom_details.ExpectedAndActual(
            _expected_file_names_renderer(self._applier.files_condition),
            custom_details.string_list(_files_in_model_list(self._actual)),
            details.HeaderAndValue(
                common.UNEXPECTED_NAME,
                details.String(self._unexpected_file.relative_to_root_dir),
            )
        )
        return Node(self._applier.name,
                    False,
                    renderer.render(),
                    (),
                    )


def _expected_file_names_renderer(expected: FilesCondition) -> DetailsRenderer:
    return custom_details.string_list(sorted(expected.files.keys()))


def _files_in_model_list(files: List[FileModel]) -> Iterable[str]:
    return sorted(
        str(fm.relative_to_root_dir)
        for fm in files
    )
