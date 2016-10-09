import os
import pathlib
import shlex

from exactly_lib.act_phase_setups import utils
from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError, \
    ActSourceAndExecutorConstructor, ActSourceAndExecutor
from exactly_lib.execution.act_phase_handling_utils import ConstructorAdapterForActSourceExecutor, \
    ActSourceAndExecutorAdapterForActSourceExecutor
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.instructions.act.executable_file import ExecutableFileInstruction
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.parse import SectionElementParser
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForStandardCommentAndEmptyLines
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder, ActSourceBuilderForStatementLines
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util import line_source
from exactly_lib.util.std import StdFiles


class _ActPhaseParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> ActPhaseInstruction:
        return ExecutableFileInstruction(source.first_line.text)


def act_phase_setup(parser: SectionElementParser = _ActPhaseParser()) -> ActPhaseSetup:
    act_source_executor = ActSourceExecutorForSingleCommand()
    return ActPhaseSetup(parser,
                         _script_source_builder,
                         act_source_executor,
                         ConstructorAdapterForActSourceExecutor(act_source_executor))


def _script_source_builder() -> ActSourceBuilder:
    return ActSourceBuilderForStatementLines()


class Constructor(ActSourceAndExecutorConstructor):
    def apply(self,
              environment: GlobalEnvironmentForPreEdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        return ActSourceAndExecutorAdapterForActSourceExecutor(act_phase_instructions,
                                                               ActSourceExecutorForSingleCommand())


class ActSourceExecutorForSingleCommand(ActSourceExecutor):
    def validate_pre_eds(self,
                         script_builder: ActSourceBuilder,
                         home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def validate(self,
                 home_dir: pathlib.Path,
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        num_source_lines = len(source.source_lines)
        if num_source_lines != 1:
            header = 'There must be a single command. Found {}'.format(num_source_lines)
            msg = header
            if num_source_lines > 0:
                msg = os.linesep.join([header + ':'] + source.source_lines)
            return svh.new_svh_validation_error(msg)
        if source.source_lines[0].isspace():
            msg = 'command is only white space'
            return svh.new_svh_validation_error(msg)
        return svh.new_svh_success()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        command_string = source_setup.script_builder.source_lines[0]
        cmd_and_args = shlex.split(command_string)
        return utils.execute_cmd_and_args(cmd_and_args,
                                          std_files)
