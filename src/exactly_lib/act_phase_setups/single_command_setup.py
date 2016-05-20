import os
import pathlib
import shlex

from exactly_lib.act_phase_setups import utils
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.instructions.act.executable_file import ExecutableFileInstruction
from exactly_lib.section_document.parse import SectionElementParser
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForStandardCommentAndEmptyLines
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.phase_setup import ActSourceExecutor, SourceSetup, ActPhaseSetup
from exactly_lib.test_case.phases.act.script_source import ActSourceBuilder
from exactly_lib.test_case.phases.act.script_source import ScriptLanguage
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util import line_source
from exactly_lib.util.std import StdFiles


class _ActPhaseParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> ActPhaseInstruction:
        return ExecutableFileInstruction(source.first_line.text)


def act_phase_setup(parser: SectionElementParser = _ActPhaseParser()) -> ActPhaseSetup:
    return ActPhaseSetup(parser,
                         _script_source_builder,
                         _ActSourceExecutorForSingleCommand())


def _script_source_builder() -> ActSourceBuilder:
    return ActSourceBuilder(_ScriptLanguage())


class _ScriptLanguage(ScriptLanguage):
    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        return []


class _ActSourceExecutorForSingleCommand(ActSourceExecutor):
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
                eds: ExecutionDirectoryStructure):
        pass

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        command_string = source_setup.script_builder.source_lines[0]
        cmd_and_args = shlex.split(command_string)
        return utils.execute_cmd_and_args(cmd_and_args,
                                          std_files)
