from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions, negation_of_assertion
from exactly_lib.instructions.assert_.utils.expression import comparison_structures
from exactly_lib.instructions.assert_.utils.expression import instruction
from exactly_lib.instructions.assert_.utils.expression import parse
from exactly_lib.instructions.assert_.utils.expression.parse import parse_integer_comparison_operator_and_rhs
from exactly_lib.instructions.utils.err_msg.property_description import \
    property_descriptor_with_just_a_constant_name
from exactly_lib.instructions.utils.parse.token_stream_parse_prime import new_token_parser
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


_PROPERTY_NAME = 'exit code'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'INTEGER': parse.INTEGER_ARGUMENT.name,
            'OPERATOR': parse.OPERATOR_ARGUMENT.name,
            'EXIT_CODE': _PROPERTY_NAME,
        })

    def single_line_description(self) -> str:
        return 'Tests the ' + _PROPERTY_NAME

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                negation_of_assertion.optional_negation_argument_usage(),
                parse.MANDATORY_INTEGER_ARGUMENT,
            ]),
                self._paragraphs(_DESCRIPTION_OF_IMPLICIT_EQUALS)),

            InvokationVariant(self._cl_syntax_for_args([
                negation_of_assertion.optional_negation_argument_usage(),
                parse.MANDATORY_OPERATOR_ARGUMENT,
                parse.MANDATORY_INTEGER_ARGUMENT,
            ]),
                self._paragraphs(_DESCRIPTION_OF_COMPARISON_WITH_OPERATOR))
        ]

    def syntax_element_descriptions(self) -> list:
        return parse.syntax_element_descriptions_with_negation_operator(
            'An integer in the interval [0, 255].')


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        parser = new_token_parser(rest_of_line)
        expectation_type = parser.consume_optional_negation_operator()
        cmp_op_and_rhs = parse_integer_comparison_operator_and_rhs(parser,
                                                                   must_be_within_byte_range)
        parser.report_superfluous_arguments_if_not_at_eol()
        cmp_setup = comparison_structures.ComparisonHandler(
            property_descriptor_with_just_a_constant_name(_PROPERTY_NAME),
            expectation_type,
            ExitCodeResolver(),
            cmp_op_and_rhs.operator,
            cmp_op_and_rhs.right_operand)
        return instruction.Instruction(cmp_setup)


class ExitCodeResolver(comparison_structures.OperandResolver):
    def __init__(self):
        super().__init__(_PROPERTY_NAME)

    def resolve(self, environment: InstructionEnvironmentForPostSdsStep):
        sds = environment.sds
        try:
            f = sds.result.exitcode_file.open()
        except IOError:
            rel_path = sds.relative_to_sds_root(sds.result.exitcode_file)
            raise return_pfh_via_exceptions.PfhHardErrorException(
                'Cannot read {exit_code} from file {file}'.format(
                    exit_code=_PROPERTY_NAME,
                    file=str(rel_path)))
        try:
            contents = f.read()
            return int(contents)
        except IOError:
            raise return_pfh_via_exceptions.PfhHardErrorException(
                'Failed to read contents from %s' % str(sds.result.exitcode_file))
        except ValueError:
            msg = 'The contents of the file for {exit_code} ("{file}") is not an integer: "{contents}"'.format(
                exit_code=_PROPERTY_NAME,
                file=str(sds.result.exitcode_file),
                contents=contents)
            raise return_pfh_via_exceptions.PfhHardErrorException(msg)
        finally:
            f.close()


def must_be_within_byte_range(actual: int) -> str:
    if actual < 0 or actual > 255:
        return 'Argument must be an integer in the interval [0, 255]\n\nFound : ' + str(actual)
    return None


_DESCRIPTION_OF_IMPLICIT_EQUALS = """\
PASS if, and only if, the {EXIT_CODE} is exactly {INTEGER}.
"""

_DESCRIPTION_OF_COMPARISON_WITH_OPERATOR = """\
PASS if, and only if, the given expression evaluates to True.

The actual {EXIT_CODE} is the left operand.
"""
