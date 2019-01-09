import unittest

from exactly_lib.definitions.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.test_configuration import \
    TestConfigurationForMatcher
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check, model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.model_construction import ModelBuilder
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, expectation_type_config__non_is_success
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    nothing__if_positive__not_option__if_negative
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


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
            maybe_not=nothing__if_positive__not_option__if_negative(expectation_type),
            num_lines=matcher_options.NUM_LINES_ARGUMENT,
            operator=self.operator,
            operand=self.operand,
            superfluous_args_str=superfluous_args_str,
        )


class TestCaseBase(unittest.TestCase):
    _CONFIGURATION = TestConfigurationForMatcher()

    @property
    def configuration(self) -> TestConfigurationForMatcher:
        return self._CONFIGURATION

    def shortDescription(self):
        return str(type(self.configuration))

    def _check_single_expression_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expectation_type: ExpectationType,
            model: ModelBuilder,
            arrangement: integration_check.ArrangementPostAct,
            expectation: Expectation):

        args_variant = args_variant_constructor.construct(expectation_type)
        complete_instruction_arguments = self.configuration.arguments_for(args_variant)

        for source in equivalent_source_variants__with_source_check__multi_line(self, complete_instruction_arguments):
            integration_check.check(
                self,
                self.configuration.new_parser(),
                source,
                model,
                arrangement=arrangement,
                expectation=expectation,
            )

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expected_result_of_positive_test: PassOrFail,
            actual_file_contents: str,
            symbols: SymbolTable = None,
            expected_symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        for expectation_type in ExpectationType:
            etc = expectation_type_config__non_is_success(expectation_type)
            with self.subTest(expectation_type=expectation_type):

                args_variant = args_variant_constructor.construct(expectation_type)
                complete_instruction_arguments = self.configuration.arguments_for(args_variant)

                for source in equivalent_source_variants__with_source_check__multi_line(self,
                                                                                        complete_instruction_arguments):
                    integration_check.check(
                        self,
                        self.configuration.new_parser(),
                        source,
                        model_construction.model_of(actual_file_contents),
                        arrangement=
                        self.configuration.arrangement_for_contents(
                            post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                            symbols=symbols),
                        expectation=
                        Expectation(
                            main_result=etc.main_result(expected_result_of_positive_test),
                            symbol_usages=expected_symbol_usages)
                    )
