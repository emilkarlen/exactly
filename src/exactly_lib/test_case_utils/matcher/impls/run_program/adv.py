from typing import Callable, Generic

from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import matcher
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner, MODEL
from exactly_lib.test_case_utils.program_execution.exe_wo_transformation import ExecutionResultAndStderr
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatcherAdv
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.program.program import Program, ProgramAdv
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class Matcher(Generic[MODEL], MatcherImplBase[MODEL]):
    NAME = ' '.join((matcher.RUN_PROGRAM,
                     syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 runner: Runner[MODEL],
                 matcher_program: Program,
                 ):
        super().__init__()
        self._runner = runner
        self._matcher_program = matcher_program

    @staticmethod
    def new_structure_tree(program: StructureRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            Matcher.NAME,
            None,
            (custom_details.TreeStructure(program),),
            (),
        )

    @property
    def name(self) -> str:
        return self.NAME

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        program_for_model = self._runner.program_for_model(self._matcher_program, model)
        exe_result = self._runner.run(program_for_model, model)
        return MatchingResult(
            exe_result.exit_code == 0,
            _ResultRenderer(self._new_tb(program_for_model),
                            exe_result)
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._matcher_program.structure())

    def _new_tb(self, program: Program) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(
            custom_details.TreeStructure(program.structure())
        )


class _ResultRenderer(NodeRenderer[bool]):
    OUTPUT_ON_STDERR_HEADER = 'Output on ' + misc_texts.STDERR
    EXIT_CODE_HEADER = misc_texts.EXIT_CODE_TITLE

    def __init__(self,
                 trace_builder_w_program_spec: TraceBuilder,
                 result: ExecutionResultAndStderr,
                 ):
        self._trace_builder = trace_builder_w_program_spec
        self._result = result

    def render(self) -> Node[bool]:
        exit_code = self._result.exit_code
        tb = self._trace_builder

        tb.append_details(
            custom_details.actual__custom(
                self.EXIT_CODE_HEADER,
                details.String(exit_code),
            )
        )
        if exit_code != 0 and self._result.stderr_contents:
            tb.append_details(
                details.HeaderAndValue(
                    self.OUTPUT_ON_STDERR_HEADER,
                    details.PreFormattedString(self._result.stderr_contents),
                )
            )

        return tb.build_bool(exit_code == 0).render()


class Adv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self,
                 mk_runner: Callable[[ApplicationEnvironment], Runner[MODEL]],
                 program: ProgramAdv,
                 ):
        self._program = program
        self._mk_runner = mk_runner

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return Matcher(
            self._mk_runner(environment),
            self._program.primitive(environment)
        )
