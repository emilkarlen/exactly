import operator
import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.assert_phase.utils import instruction_utils
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction

DESCRIPTION = Description(
    'Test numerical exitcode',
    '',
    [InvokationVariant('INTEGER',
                       'Passes iff the exit code is exactly INTEGER'),
     InvokationVariant('OPERATOR INTEGER',
                       """Passes iff the given expression,
                       with the actual exit code as an implicit left operand,
                       evaluates to True.

                       Operators: !, !=, =, <, <=, >, >=
                       """)
     ])


class InstructionForExactValue(instruction_utils.InstructionWithoutValidationBase):
    def __init__(self,
                 expected_value: int):
        self._expected_value = expected_value

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(global_environment.eds)
        if actual_value == self._expected_value:
            return pfh.new_pfh_pass()
        return pfh.new_pfh_fail('Unexpected exitcode. Expected:%d, actual:%d' % (self._expected_value,
                                                                                 actual_value))


class InstructionForOperator(instruction_utils.InstructionWithoutValidationBase):
    def __init__(self,
                 operator_info,
                 value: int):
        self._value = value
        self._operator_info = operator_info

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(global_environment.eds)
        if self._operator_info[1](actual_value, self._value):
            return pfh.new_pfh_pass()
        condition_str = self._operator_info[0] + ' ' + str(self._value)
        return pfh.new_pfh_fail('Unexpected exitcode. Expected:%s½, actual:%d' % (condition_str,
                                                                                  actual_value))


class Parser(SingleInstructionParser):
    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> AssertPhaseInstruction:
        argument_list = shlex.split(instruction_argument)
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


operators = {'!': operator.ne,
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
