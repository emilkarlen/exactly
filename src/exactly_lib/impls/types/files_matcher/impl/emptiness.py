from typing import Sequence, List

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.files_matcher.impl.base_class import FilesMatcherImplBase
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.files_matcher import FileModel, FilesMatcherModel
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.str_ import str_constructor


def emptiness_matcher() -> FilesMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(_EmptinessMatcher())


class _EmptinessMatcher(FilesMatcherImplBase):
    NAME = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @staticmethod
    def new_structure_tree() -> StructureRenderer:
        return renderers.header_only(_EmptinessMatcher.NAME)

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return self.NAME

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree()

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
            str_constructor.FormatPositional(
                'Actual contents ({} files)', len(self._actual_contents),
            ),
            custom_details.string_list(self._dir_contents_err_msg_lines()),

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
