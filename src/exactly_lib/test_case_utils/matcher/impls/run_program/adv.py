from typing import Generic

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import matcher
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
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
from exactly_lib.util.process_execution.executors.read_stderr_on_error import Result, \
    ExecutorThatReadsStderrOnNonZeroExitCode
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ExecutableExecutor


class Matcher(Generic[MODEL], MatcherImplBase[MODEL]):
    NAME = ' '.join((matcher.RUN_PROGRAM,
                     syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 application_environment: ApplicationEnvironment,
                 run_conf: RunConfiguration[MODEL],
                 matcher_program: Program,
                 ):
        super().__init__()
        self._application_environment = application_environment
        self._run_conf = run_conf
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
        program_for_model = self._run_conf.program_for_model(self._matcher_program, model)
        command_executor = self.__command_executor(model)
        program_structure = program_for_model.structure()

        result = command_executor.execute(
            self._application_environment.process_execution_settings,
            program_for_model.command,
            program_structure,
        )

        return MatchingResult(
            result.exit_code == 0,
            _ResultRenderer(self._new_tb(program_for_model),
                            result)
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(self._matcher_program.structure())

    def _new_tb(self, program: Program) -> TraceBuilder:
        return TraceBuilder(self.NAME).append_details(
            custom_details.TreeStructure(program.structure())
        )

    def __command_executor(self, model: MODEL) -> CommandExecutor[Result]:
        app_env = self._application_environment
        return CommandExecutor(
            app_env.os_services,
            self.__executor(ProcessExecutor(), model)
        )

    def __executor(self,
                   process_executor: ProcessExecutor,
                   model: MODEL,
                   ) -> ExecutableExecutor[Result]:
        app_env = self._application_environment
        return ExecutorThatReadsStderrOnNonZeroExitCode(
            process_executor,
            app_env.tmp_files_space,
            self._run_conf.stdin(model),
            std_err_contents.STD_ERR_TEXT_READER,
        )


class _ResultRenderer(NodeRenderer[bool]):
    OUTPUT_ON_STDERR_HEADER = 'Output on ' + misc_texts.STDERR
    EXIT_CODE_HEADER = misc_texts.EXIT_CODE_TITLE

    def __init__(self,
                 trace_builder_w_program_spec: TraceBuilder,
                 result: Result,
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
        if exit_code != 0 and self._result.stderr:
            tb.append_details(
                details.HeaderAndValue(
                    self.OUTPUT_ON_STDERR_HEADER,
                    details.PreFormattedString(self._result.stderr),
                )
            )

        return tb.build_bool(exit_code == 0).render()


class Adv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self,
                 run_conf: RunConfiguration[MODEL],
                 program: ProgramAdv,
                 ):
        self._program = program
        self._run_conf = run_conf

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return Matcher(
            environment,
            self._run_conf,
            self._program.primitive(environment)
        )
