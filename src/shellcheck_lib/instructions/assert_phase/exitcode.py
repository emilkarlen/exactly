import operator
import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_documentation import InvokationVariant, InstructionReference
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases import common as i
from shellcheck_lib.test_case.phases.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.util.string import line_separated
from shellcheck_lib.util.textformat import parse as paragraphs_parse
from shellcheck_lib.util.textformat.structure.paragraph import single_para


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
        TheInstructionReference(instruction_name))


class TheInstructionReference(InstructionReference):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Tests the exitcode.'

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'INTEGER',
                    single_para('Passes iff the exit code is exactly INTEGER')),
            InvokationVariant(
                    'OPERATOR INTEGER',
                    paragraphs_parse.normalize_and_parse(
                            """\
                            Passes iff the given expression,
                            with the actual exit code as an implicit left operand,
                            evaluates to True.

                            Operators: {}
                            """.format(', '.join(sorted(operators.keys())))))
        ]


class InstructionForExactValue(AssertPhaseInstruction):
    def __init__(self,
                 expected_value: int):
        self._expected_value = expected_value

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.eds)
        if actual_value == self._expected_value:
            return pfh.new_pfh_pass()
        return pfh.new_pfh_fail(_unexpected_exit_code_message(self._expected_value, actual_value))


class InstructionForOperator(AssertPhaseInstruction):
    def __init__(self,
                 operator_info,
                 value: int):
        self._value = value
        self._operator_info = operator_info

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.eds)
        if self._operator_info[1](actual_value, self._value):
            return pfh.new_pfh_pass()
        condition_str = self._operator_info[0] + ' ' + str(self._value)
        return pfh.new_pfh_fail(_unexpected_exit_code_message(condition_str, actual_value))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        argument_list = split_arguments_list_string(source.instruction_argument)
        num_arguments = len(argument_list)
        if num_arguments != 1 and num_arguments != 2:
            raise SingleInstructionInvalidArgumentException('1 or 2 arguments expected, got ' +
                                                            str(num_arguments))
        if num_arguments == 1:
            return self._single_argument(argument_list[0])
        else:
            return self._two_arguments(argument_list[0], argument_list[1])

    @staticmethod
    def _single_argument(argument: str) -> AssertPhaseInstruction:
        expected = _parse_int_argument(argument)
        return InstructionForExactValue(expected)

    @staticmethod
    def _two_arguments(arg1, arg2) -> AssertPhaseInstruction:
        if arg1 not in operators:
            raise SingleInstructionInvalidArgumentException('Invalid operator: ' + arg1)
        value = _parse_int_argument(arg2)
        return InstructionForOperator((arg1,
                                       operators[arg1]),
                                      value)


def _parse_int_argument(argument) -> int:
    try:
        expected = int(argument)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer')
    if expected < 0 or expected > 255:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer in the range [0, 255]')
    return expected


operators = {
    '!': operator.ne,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '=': operator.eq,
    '>=': operator.ge,
    '>': operator.gt
}


class InstructionEnvironmentError(Exception):
    def __init__(self,
                 error_message: str):
        super().__init__()
        self.error_message = error_message

    def __str__(self):
        return self.error_message


class FileOpenEnvironmentError(InstructionEnvironmentError):
    def __init__(self,
                 file_purpose: str,
                 path: pathlib.Path):
        super().__init__('Failed to open file for %s: %s' %
                         (file_purpose, str(path)))


def read_exitcode(eds: ExecutionDirectoryStructure) -> int:
    try:
        f = eds.result.exitcode_file.open()
    except IOError:
        raise FileOpenEnvironmentError('Exit Code', eds.result.exitcode_file)
    try:
        contents = f.read()
        return int(contents)
    except IOError:
        raise InstructionEnvironmentError('Failed to read contents from %s' % str(eds.result.exitcode_file))
    except ValueError:
        msg = 'The contents of the file for Exit Code ("%s") is not an integer: "%s"' % (str(eds.result.exitcode_file),
                                                                                         contents)
        raise InstructionEnvironmentError(msg)
    finally:
        f.close()


def _unexpected_exit_code_message(expected, actual_value):
    return line_separated(['Unexpected exitcode.',
                           'Expected : {}'.format(expected),
                           'Actual   : {}'.format(actual_value)])
