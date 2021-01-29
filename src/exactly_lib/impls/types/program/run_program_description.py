from typing import Callable

from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class RunProgramStructureRenderer(NodeRenderer[None]):
    def __init__(self,
                 structure_header: str,
                 ignore_exit_code: bool,
                 program: Callable[[], StructureRenderer],
                 ):
        self._structure_header = structure_header
        self._program = program
        self._ignore_exit_code = ignore_exit_code

    def render(self) -> Node[None]:
        return self._renderer().render()

    def _renderer(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self._structure_header,
            None,
            (
                custom_details.optional_option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME,
                                               self._ignore_exit_code),
                custom_details.TreeStructure(self._program()),
            ),
            (),
        )
