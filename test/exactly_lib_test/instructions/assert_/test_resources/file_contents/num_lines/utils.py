import unittest

from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail, ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class InstructionArgumentsVariantConstructor:
    """"Constructs instruction arguments for a variant of (TRANSFORMER, [!]  OPERATOR OPERAND)."""

    def __init__(self,
                 operator: str,
                 operand: str,
                 superfluous_args_str: str = '',
                 transformer: str = ''):
        self.transformer = transformer
        self.operator = operator
        self.operand = operand
        self.superfluous_args_str = superfluous_args_str

    def construct(self, expectation_type: ExpectationType) -> str:
        transformation = ''
        if self.transformer:
            transformation = option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME) + ' ' + self.transformer

        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str

        return '{transformation} {maybe_not} {num_lines} {operator} {operand}{superfluous_args_str}'.format(
            transformation=transformation,
            maybe_not=ExpectationTypeConfig(expectation_type).nothing__if_positive__not_option__if_negative,
            num_lines=instruction_options.NUM_LINES_ARGUMENT,
            operator=self.operator,
            operand=self.operand,
            superfluous_args_str=superfluous_args_str,
        )


class TestCaseBase(unittest.TestCase):
    def __init__(self, configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self.configuration))

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expected_result_of_positive_test: PassOrFail,
            actual_file_contents: str,
            symbols: SymbolTable = None,
            expected_symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        for expectation_type in ExpectationType:
            etc = ExpectationTypeConfig(expectation_type)
            with self.subTest(expectation_type=expectation_type):

                args_variant = args_variant_constructor.construct(expectation_type)
                complete_instruction_arguments = self.configuration.first_line_argument(args_variant)

                for source in equivalent_source_variants__with_source_check(self, complete_instruction_arguments):
                    instruction_check.check(
                        self,
                        self.configuration.new_parser(),
                        source,
                        arrangement=
                        self.configuration.arrangement_for_contents(
                            actual_file_contents,
                            post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                            symbols=symbols),
                        expectation=
                        Expectation(
                            main_result=etc.main_result(expected_result_of_positive_test),
                            symbol_usages=expected_symbol_usages)
                    )
