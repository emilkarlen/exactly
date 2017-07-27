import operator as py_operator_fun
import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.misc_utils import new_token_stream
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse.token import Token
from exactly_lib.util.string import line_separated


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


INTEGER_ARGUMENT = a.Named('INTEGER')
OPERATOR_ARGUMENT = a.Named('OPERATOR')


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.integer_arg = a.Single(a.Multiplicity.MANDATORY,
                                    INTEGER_ARGUMENT)
        self.op_arg = a.Single(a.Multiplicity.MANDATORY,
                               OPERATOR_ARGUMENT)
        super().__init__(name, {
            'INTEGER': INTEGER_ARGUMENT.name,
            'OPERATOR': OPERATOR_ARGUMENT.name,
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
        operators_list = ', '.join(sorted(OPERATORS.keys()))
        operator_text = 'One of: ' + operators_list + '.'
        integer_text = 'An integer in the interval [0, 255].'
        return [
            SyntaxElementDescription(INTEGER_ARGUMENT.name,
                                     self._paragraphs(integer_text)),
            SyntaxElementDescription(OPERATOR_ARGUMENT.name,
                                     self._paragraphs(operator_text))
        ]


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        token_stream = new_token_stream(rest_of_line)
        if token_stream.is_null:
            raise SingleInstructionInvalidArgumentException('Missing arguments')
        arg1 = token_stream.consume()
        if arg1.is_plain and arg1.string in OPERATORS:
            instruction = self._two_arguments(arg1.string, token_stream)
        else:
            instruction = self._single_argument(arg1)
        if not token_stream.is_null:
            msg = 'Superfluous arguments: ' + token_stream.remaining_part_of_current_line
            raise SingleInstructionInvalidArgumentException(msg)
        return instruction

    @staticmethod
    def _single_argument(value_token: Token) -> AssertPhaseInstruction:
        value_resolver = _string_resolver_of(value_token)
        return InstructionForExactValue(value_resolver)

    @staticmethod
    def _two_arguments(operator_string, remaining_arguments: TokenStream) -> AssertPhaseInstruction:
        if remaining_arguments.is_null:
            raise SingleInstructionInvalidArgumentException('Missing {INTEGER} argument.'.format(
                INTEGER=INTEGER_ARGUMENT))
        value_token = remaining_arguments.consume()
        value_resolver = _string_resolver_of(value_token)
        return InstructionForOperator((operator_string,
                                       OPERATORS[operator_string]),
                                      value_resolver)


class InstructionBase(AssertPhaseInstruction):
    def __init__(self,
                 value_resolver: StringResolver):
        self._value_resolver = value_resolver

    def symbol_usages(self) -> list:
        return self._value_resolver.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPostSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        value_string = self._value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        try:
            expected = int(value_string)
        except ValueError:
            return svh.new_svh_validation_error('Argument must be an integer: `{}\''.format(value_string))
        if expected < 0 or expected > 255:
            return svh.new_svh_validation_error('Argument must be an integer in the interval [0, 255]')
        return svh.new_svh_success()

    def _resolved_value(self,
                        environment: i.InstructionEnvironmentForPostSdsStep,
                        ) -> int:
        value_string = self._value_resolver.resolve(environment.symbols).value_when_no_dir_dependencies()
        return int(value_string)


class InstructionForExactValue(InstructionBase):
    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.sds)
        value = self._resolved_value(environment)
        if actual_value == value:
            return pfh.new_pfh_pass()
        return pfh.new_pfh_fail(_unexpected_exit_code_message(value, actual_value))


class InstructionForOperator(InstructionBase):
    def __init__(self,
                 operator_info,
                 value_resolver: StringResolver):
        super().__init__(value_resolver)
        self._operator_info = operator_info

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_value = read_exitcode(environment.sds)
        value = self._resolved_value(environment)
        if self._operator_info[1](actual_value, value):
            return pfh.new_pfh_pass()
        condition_str = self._operator_info[0] + ' ' + str(value)
        return pfh.new_pfh_fail(_unexpected_exit_code_message(condition_str, actual_value))


def _string_resolver_of(value_token: Token) -> StringResolver:
    return parse_string.parse_string_resolver_from_token(
        value_token,
        string_made_up_by_just_strings(
            'The {INTEGER} argument must be made up of just {string_type} values.'.format(
                INTEGER=INTEGER_ARGUMENT.name,
                string_type=help_texts.TYPE_INFO_DICT[ValueType.STRING].type_name,
            )
        ))


def _parse_int_argument(argument) -> int:
    try:
        expected = int(argument)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer')
    if expected < 0 or expected > 255:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer in the interval [0, 255]')
    return expected


OPERATORS = {
    '!': py_operator_fun.ne,
    '!=': py_operator_fun.ne,
    '<': py_operator_fun.lt,
    '<=': py_operator_fun.le,
    '=': py_operator_fun.eq,
    '>=': py_operator_fun.ge,
    '>': py_operator_fun.gt
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
