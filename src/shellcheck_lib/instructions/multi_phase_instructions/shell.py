from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.utils.sub_process_execution import ExecutorThatLogsResultUnderPhaseDir, \
    InstructionSourceInfo, InstructionMetaInfo, ExecuteInfo, \
    ResultAndStderr, execute_and_read_stderr_if_non_zero_exitcode, result_to_sh, result_to_pfh
from shellcheck_lib.test_case.instruction_description import Description, InvokationVariant
from shellcheck_lib.test_case.sections.common import TestCaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh


class TheDescriptionBase(Description):
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
                    single_para('A plain file.')),
        ]


class DescriptionForNonAssertPhaseInstruction(TheDescriptionBase):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        return single_para('The assertion passes if (and only if) the exit code from the command is 0.')


class Parser(SingleInstructionParser):
    def __init__(self,
                 instruction_meta_info: InstructionMetaInfo,
                 executor_2_instruction_function):
        self.instruction_meta_info = instruction_meta_info
        self.executor_2_instruction_function = executor_2_instruction_function

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        execute_info = ExecuteInfo(InstructionSourceInfo(self.instruction_meta_info,
                                                         source.line_sequence.first_line.line_number),
                                   arguments)
        return self.executor_2_instruction_function(execute_info)


def run(execute_info: ExecuteInfo,
        eds: ExecutionDirectoryStructure) -> ResultAndStderr:
    executor = ExecutorThatLogsResultUnderPhaseDir(is_shell=True)
    return execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, eds)


def run_and_return_sh(execute_info: ExecuteInfo,
                      eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
    result = run(execute_info, eds)
    return result_to_sh(result)


def run_and_return_pfh(execute_info: ExecuteInfo,
                       eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
    result = run(execute_info, eds)
    return result_to_pfh(result)
