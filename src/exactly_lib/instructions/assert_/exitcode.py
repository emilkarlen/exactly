import operator
import pathlib

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.string import line_separated


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    _INTEGER_ARGUMENT = a.Named('INTEGER')
    _OPERATOR_ARGUMENT = a.Named('OPERATOR')

    def __init__(self, name: str):
        self.integer_arg = a.Single(a.Multiplicity.MANDATORY,
                                    self._INTEGER_ARGUMENT)
        self.op_arg = a.Single(a.Multiplicity.MANDATORY,
                               self._OPERATOR_ARGUMENT)
        super().__init__(name, {
            'INTEGER': self._INTEGER_ARGUMENT.name,
            'OPERATOR': self._OPERATOR_ARGUMENT.name,
        })

    def single_line_description(self) -> str:
        return 'Tests the exit code'

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([self.integer_arg]),
                              self._paragraphs(
                                  """\
                                  PASS if, and only if, the exit code is exactly {INTEGER}.
                                  """)),
            InvokationVariant(self._cl_syntax_for_args([self.op_arg, self.integer_arg]),
                              self._paragraphs(
                                  """\
                                  PASS if, and only if, the given expression evaluates to True.

                                  The actual exit code is the left operand.
                                  """))
        ]

    def syntax_element_descriptions(self) -> list:
        operators_list = ', '.join(sorted(operators.keys()))
        operator_text = 'One of: ' + operators_list + '.'
        integer_text = 'An integer in the interval [0, 255].'
        return [
            SyntaxElementDescription(self._INTEGER_ARGUMENT.name,
                                     self._paragraphs(integer_text)),
            SyntaxElementDescription(self._OPERATOR_ARGUMENT.name,
                                     self._paragraphs(operator_text))
        ]


class InstructionForExactValue(AssertPhaseInstruction):
    def __init__(self,
                 expected_value: int):
        self._expected_value = expected_value

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.sds)
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
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.sds)
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
        raise SingleInstructionInvalidArgumentException('Argument must be an integer in the interval [0, 255]')
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


def read_exitcode(sds: SandboxDirectoryStructure) -> int:
    try:
        f = sds.result.exitcode_file.open()
    except IOError:
        raise FileOpenEnvironmentError('Exit Code', sds.result.exitcode_file)
    try:
        contents = f.read()
        return int(contents)
    except IOError:
        raise InstructionEnvironmentError('Failed to read contents from %s' % str(sds.result.exitcode_file))
    except ValueError:
        msg = 'The contents of the file for Exit Code ("%s") is not an integer: "%s"' % (str(sds.result.exitcode_file),
                                                                                         contents)
        raise InstructionEnvironmentError(msg)
    finally:
        f.close()


def _unexpected_exit_code_message(expected, actual_value):
    return line_separated(['Unexpected exitcode.',
                           'Expected : {}'.format(expected),
                           'Actual   : {}'.format(actual_value)])
