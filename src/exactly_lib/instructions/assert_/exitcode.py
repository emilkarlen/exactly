from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.element_parsers.token_stream_parser import new_token_parser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.condition import comparison_structures, instruction
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    parse_integer_comparison_operator_and_rhs
from exactly_lib.test_case_utils.err_msg.property_description import \
    property_descriptor_with_just_a_constant_name
from exactly_lib.util.messages import expected_found

_OPERAND_DESCRIPTION = 'An integer in the interval [0, 255]'


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


_PROPERTY_NAME = 'exit code'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name, {
            'INTEGER_COMPARISON': syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.argument.name,
            'EXIT_CODE': _PROPERTY_NAME,
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
        })

    def single_line_description(self) -> str:
        return 'Tests the ' + _PROPERTY_NAME

    def main_description_rest(self) -> list:
        return self._tp.fnap(_MAIN_DESCRIPTION)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                negation_of_predicate.optional_negation_argument_usage(),
                syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.single_mandatory,
            ])),
        ]

    def see_also_targets(self) -> list:
        return [
            syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.cross_reference_target
        ]


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
        except IOError:
            raise return_pfh_via_exceptions.PfhHardErrorException(
                'Failed to read contents from ' + str(sds.result.exitcode_file))
        finally:
            f.close()

        try:
            return int(contents)
        except ValueError:
            msg = 'The contents of the file for {exit_code} ("{file}") is not an integer: "{contents}"'.format(
                exit_code=_PROPERTY_NAME,
                file=str(sds.result.exitcode_file),
                contents=contents)
            raise return_pfh_via_exceptions.PfhHardErrorException(msg)


def must_be_within_byte_range(actual: int) -> str:
    if actual < 0 or actual > 255:
        return expected_found.unexpected_lines(_OPERAND_DESCRIPTION,
                                               str(actual))
    return None


_MAIN_DESCRIPTION = """\
{PASS} if, and only if, the {EXIT_CODE} satisfies {INTEGER_COMPARISON}.
"""
