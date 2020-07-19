from typing import Generic

from exactly_lib.common.err_msg import std_err_contents
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import matcher
from exactly_lib.test_case_utils.matcher.impls.impl_base_class import MatcherImplBase
from exactly_lib.test_case_utils.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.test_case_utils.program_execution import command_executors
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatcherAdv
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.program.program import Program, ProgramAdv
from exactly_lib.util.process_execution.executors.read_stderr_on_error import Result, \
    ExecutorThatReadsStderrOnNonZeroExitCode
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ExecutableExecutor
from . import trace


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

    @property
    def name(self) -> str:
        return trace.TheStructureRenderer.NAME

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        program_for_model = self._run_conf.program_for_model(self._matcher_program, model)
        command_executor = self._command_executor(model)
        program_structure = program_for_model.structure()

        result = command_executor.execute(
            self._application_environment.process_execution_settings,
            program_for_model.command,
            program_structure,
        )

        return MatchingResult(
            result.exit_code == 0,
            trace.TheTraceRenderer(program_for_model.structure(),
                                   result)
        )

    def _structure(self) -> StructureRenderer:
        return trace.TheStructureRenderer(self._matcher_program.structure())

    def _command_executor(self, model: MODEL) -> CommandExecutor[Result]:
        app_env = self._application_environment
        return command_executors.executor_that_raises_hard_error(
            app_env.os_services,
            self._executor(ProcessExecutor(), model)
        )

    def _executor(self,
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
