from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase
from exactly_lib.instructions.utils.main_step_executor import MainStepExecutor, InstructionParts
from exactly_lib.instructions.utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.instructions.utils.sub_process_execution import ExecutorThatStoresResultInFilesInDir, \
    InstructionSourceInfo, ExecuteInfo, \
    ResultAndStderr, execute_and_read_stderr_if_non_zero_exitcode, result_to_sh, result_to_pfh
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import TestCaseInstruction, PhaseLoggingPaths, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a

_COMMAND_SYNTAX_ELEMENT = 'COMMAND'


class TheInstructionDocumentationBase(InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase):
    def __init__(self, name: str):
        super().__init__(name, {'COMMAND': _COMMAND_SYNTAX_ELEMENT})
        self.command_arg = a.Named(_COMMAND_SYNTAX_ELEMENT)

    def single_line_description(self) -> str:
        return "Executes a command using the current system's shell"

    def _main_description_rest_body(self) -> list:
        text = """\
        Which commands are available and the syntax of them depends
        on the current system's shell and environment.


        The shell takes care of interpreting {COMMAND}, so all features of the
        shell can be used.


        Use of the {instruction_name} instruction is not portable since it
        uses the current operating system environment's shell.


        On POSIX, the shell defaults to /bin/sh.

        On Windows, the COMSPEC environment variable specifies the default shell.
        """
        return self._paragraphs(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.command_arg)]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        text = """\
        Something that is understood by the current system's shell.
        """
        return [
            SyntaxElementDescription(self.command_arg.name,
                                     self._paragraphs(text))
        ]


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name)

    def _main_description_rest_prelude(self) -> list:
        text = """\
        It is considered an error if {COMMAND} exits with a non-zero exit code.
        """
        return self._paragraphs(text)


class Parser(SingleInstructionParser):
    def __init__(self,
                 instruction_name: str,
                 instruction_setup_2_instruction_function):
        self.instruction_name = instruction_name
        self.instruction_setup_2_instruction_function = instruction_setup_2_instruction_function

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = _COMMAND_SYNTAX_ELEMENT + ' must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        execute_info = ExecuteInfo(InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                         self.instruction_name),
                                   arguments)
        instruction_setup = InstructionParts(ConstantSuccessValidator(),
                                             ShellMainStepExecutor(execute_info))
        return self.instruction_setup_2_instruction_function(instruction_setup)


def run(execute_info: ExecuteInfo,
        phase_logging_paths: PhaseLoggingPaths) -> ResultAndStderr:
    executor = ExecutorThatStoresResultInFilesInDir(is_shell=True)
    return execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, phase_logging_paths)


def run_and_return_sh(execute_info: ExecuteInfo,
                      phase_logging_paths: PhaseLoggingPaths) -> sh.SuccessOrHardError:
    result = run(execute_info, phase_logging_paths)
    return result_to_sh(result)


def run_and_return_pfh(execute_info: ExecuteInfo,
                       phase_logging_paths: PhaseLoggingPaths) -> pfh.PassOrFailOrHardError:
    result = run(execute_info, phase_logging_paths)
    return result_to_pfh(result)


class ShellMainStepExecutor(MainStepExecutor):
    def __init__(self, execute_info: ExecuteInfo):
        self.execute_info = execute_info

    def apply_sh(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 logging_paths: PhaseLoggingPaths,
                 os_services: OsServices) -> sh.SuccessOrHardError:
        return run_and_return_sh(self.execute_info, logging_paths)

    def apply_pfh(self, environment: InstructionEnvironmentForPostSdsStep,
                  logging_paths: PhaseLoggingPaths,
                  os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return run_and_return_pfh(self.execute_info, logging_paths)
