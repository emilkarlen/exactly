from typing import Sequence, List

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.description_tree import custom_details, custom_renderers
from exactly_lib.test_case_utils.files_matcher.impl.base_class import FilesMatcherImplBase
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel, FilesMatcher, \
    GenericFilesMatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util import logic_types, strings
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.logic_types import ExpectationType


def emptiness_matcher() -> FilesMatcherSdv:
    return FilesMatcherSdv(emptiness_matcher__generic())


def emptiness_matcher__generic() -> GenericFilesMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(_EmptinessMatcher(ExpectationType.POSITIVE))


class _EmptinessMatcher(FilesMatcherImplBase):
    NAME = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @staticmethod
    def new_structure_tree(expectation_type: ExpectationType) -> StructureRenderer:
        positive = renderers.header_only(_EmptinessMatcher.NAME)
        return (
            positive
            if expectation_type is ExpectationType.POSITIVE
            else
            custom_renderers.negation(positive)
        )

    def __init__(self, expectation_type: ExpectationType):
        super().__init__()
        self._expectation_type = expectation_type

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._expectation_type)

    @property
    def negation(self) -> FilesMatcher:
        return _EmptinessMatcher(logic_types.negation(self._expectation_type))

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        files_list = list(model.files())
        num_files_in_dir = len(files_list)
        if num_files_in_dir != 0:
            return MatchingResult(
                False,
                _FailureTraceRenderer(
                    self.name,
                    files_list,
                    model,
                )
            )
        else:
            return self._new_tb().build_result(True)


class _FailureTraceRenderer(NodeRenderer[bool]):
    def __init__(self,
                 matcher_name: str,
                 actual_contents: List[FileModel],
                 model: FilesMatcherModel):
        self._matcher_name = matcher_name
        self._actual_contents = actual_contents
        self._model = model

    def render(self) -> Node[bool]:
        return Node(
            self._matcher_name,
            False,
            self._details(),
            ()
        )

    def _details(self) -> Sequence[tree.Detail]:
        renderer = custom_details.actual__custom(
            strings.FormatPositional(
                'Actual contents ({} files)', len(self._actual_contents),
            ),
            custom_details.StringList(self._dir_contents_err_msg_lines()),

        )
        return renderer.render()

    def _dir_contents_err_msg_lines(self) -> List[str]:
        paths_in_dir = [
            f.relative_to_root_dir
            for f in self._actual_contents
        ]
        if len(paths_in_dir) < 50:
            paths_in_dir.sort()
        num_files_to_display = 5
        ret_val = [
            str(p)
            for p in paths_in_dir[:num_files_to_display]
        ]
        if len(self._actual_contents) > num_files_to_display:
            ret_val.append('...')
        return ret_val
