from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions
from exactly_lib.instructions.assert_.utils.expression.comprison_structures import IntegerComparisonExecutor, \
    IntegerComparisonOperatorAndRhs
from exactly_lib.instructions.assert_.utils.expression.integer_comparators import NAME_2_OPERATOR
from exactly_lib.instructions.assert_.utils.expression.parse import parse_integer_comparison_operator_and_rhs
from exactly_lib.instructions.utils.parse.token_stream_parse_prime import new_token_parser
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh, svh
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax.elements import argument as a


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
        operators_list = ', '.join(sorted(NAME_2_OPERATOR.keys()))
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
        parser = new_token_parser(rest_of_line)
        comparison_setup = parse_integer_comparison_operator_and_rhs(parser,
                                                                     must_be_within_byte_range)
        parser.report_superfluous_arguments_if_not_at_eol()
        return Instruction(comparison_setup)


class Instruction(AssertPhaseInstruction):
    def __init__(self,
                 comparison_setup: IntegerComparisonOperatorAndRhs):
        self.comparison_setup = comparison_setup

    def symbol_usages(self) -> list:
        return self.comparison_setup.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPostSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        return self.comparison_setup.validate_pre_sds(environment)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return return_pfh_via_exceptions.translate_pfh_exception_to_pfh(
            self._main_that_raises_pfh_exceptions,
            environment,
            os_services)

    def _main_that_raises_pfh_exceptions(self,
                                         environment: i.InstructionEnvironmentForPostSdsStep,
                                         os_services: OsServices):
        lhs = read_exitcode(environment.sds)
        rhs = self.comparison_setup.integer_resolver.resolve(environment)
        executor = IntegerComparisonExecutor(
            'exitcode',
            lhs,
            rhs,
            self.comparison_setup.operator)
        executor.execute_and_return_pfh_via_exceptions()


def read_exitcode(sds: SandboxDirectoryStructure) -> int:
    try:
        f = sds.result.exitcode_file.open()
    except IOError:
        rel_path = sds.relative_to_sds_root(sds.result.exitcode_file)
        raise return_pfh_via_exceptions.PfhHardErrorException(
            'Cannot read exit code from file ' + str(rel_path))
    try:
        contents = f.read()
        return int(contents)
    except IOError:
        raise return_pfh_via_exceptions.PfhHardErrorException(
            'Failed to read contents from %s' % str(sds.result.exitcode_file))
    except ValueError:
        msg = 'The contents of the file for Exit Code ("{}") is not an integer: "{}"'.format(
            str(sds.result.exitcode_file),
            contents)
        raise return_pfh_via_exceptions.PfhHardErrorException(msg)
    finally:
        f.close()


def must_be_within_byte_range(actual: int) -> str:
    if actual < 0 or actual > 255:
        return 'Argument must be an integer in the interval [0, 255]\n\nFound : ' + str(actual)
    return None
