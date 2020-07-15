from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import matcher
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.documentation import texts
from exactly_lib.type_system.description import trace_building
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.matching_result import TraceRenderer
from exactly_lib.util.description_tree import renderers, details
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.process_execution.executors.read_stderr_on_error import Result


class TheStructureRenderer(NodeRenderer[None]):
    NAME = ' '.join((matcher.RUN_PROGRAM,
                     syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))

    def __init__(self, program: StructureRenderer):
        self._program = program

    def render(self) -> Node[None]:
        return self._renderer().render()

    def _renderer(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self.NAME,
            None,
            (custom_details.TreeStructure(self._program),),
            (),
        )


class TheTraceRenderer(NodeRenderer[bool]):
    def __init__(self,
                 program: StructureRenderer,
                 result: Result,
                 ):
        self._program = program
        self._result = result

    def render(self) -> Node[bool]:
        return self._render().render()

    def _render(self) -> TraceRenderer:
        exit_code = self._result.exit_code
        tb = trace_building.TraceBuilder(TheStructureRenderer.NAME).append_details(
            custom_details.TreeStructure(self._program)
        )

        tb.append_details(
            custom_details.actual__custom(
                misc_texts.EXIT_CODE_TITLE,
                details.String(exit_code),
            )
        )
        if exit_code != 0 and self._result.stderr:
            tb.append_details(
                details.HeaderAndValue(
                    texts.OUTPUT_ON_STDERR__HEADER,
                    details.PreFormattedString(self._result.stderr),
                )
            )

        return tb.build_bool(exit_code == 0)
