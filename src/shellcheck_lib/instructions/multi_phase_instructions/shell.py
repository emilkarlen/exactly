from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation, \
    InvokationVariant
from shellcheck_lib.instructions.utils.sub_process_execution import ExecutorThatStoresResultInFilesInDir, \
    InstructionSourceInfo, ExecuteInfo, \
    ResultAndStderr, execute_and_read_stderr_if_non_zero_exitcode, result_to_sh, result_to_pfh
from shellcheck_lib.test_case.phases.common import TestCaseInstruction, PhaseLoggingPaths
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat.structure.structures import paras


class TheInstructionDocumentationBase(InstructionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return "Executes the given program using the system's shell."

    def main_description_rest(self) -> list:
        raise NotImplementedError()

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'PROGRAM ARGUMENT...',
                paras('A plain file.')),
        ]


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        return paras('The assertion passes if (and only if) the exit code from the command is 0.')


class Parser(SingleInstructionParser):
    def __init__(self,
                 instruction_name: str,
                 executor_2_instruction_function):
        self.instruction_name = instruction_name
        self.executor_2_instruction_function = executor_2_instruction_function

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        execute_info = ExecuteInfo(InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                         self.instruction_name),
                                   arguments)
        return self.executor_2_instruction_function(execute_info)


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
