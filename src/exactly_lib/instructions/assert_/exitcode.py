from typing import List, Sequence, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.element_parsers.token_stream_parser import new_token_parser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case_utils import negation_of_predicate, pfh_exception
from exactly_lib.test_case_utils.condition import comparison_structures, instruction
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import \
    parse_integer_comparison_operator_and_rhs
from exactly_lib.test_case_utils.err_msg.property_description import \
    property_descriptor_with_just_a_constant_name
from exactly_lib.util.messages import expected_found
from exactly_lib.util.simple_textstruct.rendering import strings
from exactly_lib.util.textformat.structure.core import ParagraphItem

_OPERAND_DESCRIPTION = 'An integer in the interval [0, 255]'


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


_PROPERTY_NAME = 'exit code'


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name, {
            'INTEGER_COMPARISON': syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.argument.name,
            'EXIT_CODE': _PROPERTY_NAME,
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
        })

    def single_line_description(self) -> str:
        return 'Tests the ' + _PROPERTY_NAME

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                negation_of_predicate.optional_negation_argument_usage(),
                syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.single_mandatory,
            ]),
        ]

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return [
            negation_of_predicate.assertion_syntax_element_description(),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
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


class ExitCodeResolver(comparison_structures.OperandResolver[int]):
    def __init__(self):
        super().__init__(_PROPERTY_NAME)

    def resolve_value_of_any_dependency(self, environment: PathResolvingEnvironmentPreOrPostSds) -> int:
        sds = environment.sds
        try:
            f = sds.result.exitcode_file.open()
        except IOError:
            rel_path = sds.relative_to_sds_root(sds.result.exitcode_file)
            err_msg = text_docs.single_line(
                strings.FormatMap(
                    'Cannot read {exit_code} from file {file}',
                    {
                        'exit_code': _PROPERTY_NAME,
                        'file': rel_path,
                    }
                )
            )
            raise pfh_exception.PfhHardErrorException(err_msg)
        try:
            contents = f.read()
        except IOError:
            raise pfh_exception.PfhHardErrorException(
                text_docs.single_line(
                    strings.Concatenate([
                        _FAILED_TO_READ_CONTENTS_FROM,
                        sds.result.exitcode_file,
                    ])
                ))
        finally:
            f.close()

        try:
            return int(contents)
        except ValueError:
            msg = text_docs.single_line(
                strings.FormatMap(
                    'The contents of the file for {exit_code} ("{file}") is not an integer: "{contents}"',
                    {
                        'exit_code': _PROPERTY_NAME,
                        'file': sds.result.exitcode_file,
                        'contents': contents,
                    })
            )
            raise pfh_exception.PfhHardErrorException(msg)


def must_be_within_byte_range(actual: int) -> Optional[str]:
    if actual < 0 or actual > 255:
        return expected_found.unexpected_lines(_OPERAND_DESCRIPTION,
                                               str(actual))
    return None


_MAIN_DESCRIPTION = """\
{PASS} if, and only if, the {EXIT_CODE} satisfies {INTEGER_COMPARISON}.
"""

_FAILED_TO_READ_CONTENTS_FROM = 'Failed to read contents from '
