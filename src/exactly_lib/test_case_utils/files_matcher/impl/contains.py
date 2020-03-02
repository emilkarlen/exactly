from pathlib import Path
from typing import Optional, Mapping

from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher.impl import equals_and_contains_utils as utils
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, GenericFilesMatcherSdv, FileModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


def contains_sdv(files_condition: FilesConditionSdv) -> GenericFilesMatcherSdv:
    return utils.MatcherSdvWithApplier(_CONTAINS_CONFIG, files_condition)


class _ContainsApplier(utils.Applier):
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
                                              _RendererOfNonMatchingMatcher(self.name,
                                                                            actual_file,
                                                                            matching_result))

                del expected_files[relative_file_name]

                if len(expected_files) == 0:
                    return MatchingResult(True,
                                          renderers.header_only__w_value(self.name, True))

        return MatchingResult(False,
                              _RendererOfFilesNotFound(self.name, expected_files))


_CONTAINS_CONFIG = utils.Conf(utils.CONTAINS_STRUCTURE_NAME,
                              _ContainsApplier)


class _RendererOfNonMatchingMatcher(NodeRenderer[bool]):
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


class _RendererOfFilesNotFound(NodeRenderer[bool]):
    def __init__(self,
                 name: str,
                 files_not_found: Mapping[Path, Optional[FileModel]],
                 ):
        self._name = name
        self._files_not_found = files_not_found

    def render(self) -> Node[bool]:
        return Node.empty(self._name, False)
