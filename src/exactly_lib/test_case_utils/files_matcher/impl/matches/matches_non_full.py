import pathlib
from pathlib import Path
from typing import Optional, Mapping, List

from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv
from exactly_lib.test_case_utils.files_matcher.impl.matches import common
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdv, FileModel
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node


def sdv(files_condition: FilesConditionSdv) -> FilesMatcherSdv:
    return common.MatcherSdvWithApplier(_CONTAINS_CONFIG, files_condition)


class _Applier(common.Applier):
    def apply(self) -> MatchingResult:
        if len(self.files_condition.files) == 0:
            return self._result_true()

        expected_files = {
            Path(posix_path): mb_fm
            for posix_path, mb_fm in self.files_condition.files.items()
        }

        files_found = []

        for actual_file in self.model.files():
            relative_file_name = actual_file.relative_to_root_dir
            if relative_file_name in expected_files:
                mb_matcher = expected_files[relative_file_name]
                if mb_matcher is not None:
                    matching_result = mb_matcher.matches_w_trace(actual_file.as_file_matcher_model())
                    if not matching_result.value:
                        return MatchingResult(
                            False,
                            common.RendererOfNonMatchingFileMatcher(self.name,
                                                                    actual_file.relative_to_root_dir,
                                                                    matching_result))

                files_found.append(relative_file_name)
                del expected_files[relative_file_name]

                if len(expected_files) == 0:
                    return self._result_true()

        return MatchingResult(False,
                              _RendererOfFilesNotFound(self.name, files_found, expected_files))


_CONTAINS_CONFIG = common.Conf(common.MATCHES_NON_FULL__STRUCTURE_NAME,
                               _Applier)


class _RendererOfFilesNotFound(NodeRenderer[bool]):
    def __init__(self,
                 name: str,
                 files_found: List[pathlib.Path],
                 files_not_found: Mapping[Path, Optional[FileModel]],
                 ):
        self._name = name
        self._files_found = files_found
        self._files_not_found = files_not_found

    def render(self) -> Node[bool]:
        return Node(
            self._name,
            False,
            self._details().render(),
            (),
        )

    def _details(self) -> DetailsRenderer:
        parts = []

        if self._files_found:
            parts.append(
                custom_details.HeaderAndValue(
                    common.FILES_FOUND,
                    custom_details.string_list(self._files_found)
                ),
            )

        parts.append(
            custom_details.HeaderAndValue(
                common.FILES_NOT_FOUND,
                custom_details.string_list(sorted(self._files_not_found.keys()))
            )
        )

        return details.SequenceRenderer(parts)
