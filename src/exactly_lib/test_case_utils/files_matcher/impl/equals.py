from pathlib import PurePosixPath
from typing import List, Optional

from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher.impl import equals_and_contains_utils as utils
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcher, GenericFilesMatcherSdv, \
    FileModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


def equals_sdv(files_condition: FilesConditionSdv) -> GenericFilesMatcherSdv:
    return utils.MatcherSdvWithApplier(_EQUALS_CONFIG, files_condition)


class _NameMatch:
    def __init__(self,
                 fc_path: PurePosixPath,
                 fc_matcher: Optional[FilesMatcher],
                 match_from_model: FileModel,
                 ):
        self.fc_path = fc_path
        self.fc_matcher = fc_matcher
        self.match_from_model = match_from_model


class _EqualsApplier(utils.Applier):
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
                                      _RendererOfUnexpectedFile(actual_file, self))

        return self._continue_w_file_matcher_check(name_matches)

    def _continue_w_file_matcher_check(self, files: List[_NameMatch]) -> MatchingResult:
        for name_match in files:
            if name_match.fc_matcher is not None:
                file_model = name_match.match_from_model.as_file_matcher_model()
                matching_result = name_match.fc_matcher.matches_w_trace(file_model)
                if not matching_result.value:
                    return MatchingResult(False, _RendererOfNonMatchingFileMatcher(name_match,
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
        return MatchingResult(False, _RendererOfUnexpectedNumFiles(fetched, self))


_EQUALS_CONFIG = utils.Conf(utils.EQUALS_STRUCTURE_NAME,
                            _EqualsApplier)


class _RendererOfUnexpectedNumFiles(NodeRenderer[bool]):
    def __init__(self,
                 fetch_of_expected_plus_1: List[FileModel],
                 applier: _EqualsApplier,
                 ):
        self._fetch_of_expected_plus_1 = fetch_of_expected_plus_1
        self._applier = applier

    def render(self) -> Node[bool]:
        return Node.empty(self._applier.name, False)


class _RendererOfUnexpectedFile(NodeRenderer[bool]):
    def __init__(self,
                 unexpected_file: FileModel,
                 applier: _EqualsApplier,
                 ):
        self._unexpected_file = unexpected_file
        self._applier = applier

    def render(self) -> Node[bool]:
        return Node.empty(self._applier.name, False)


class _RendererOfNonMatchingFileMatcher(NodeRenderer[bool]):
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
