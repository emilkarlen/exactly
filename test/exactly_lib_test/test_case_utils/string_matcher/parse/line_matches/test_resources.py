import unittest

from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.test_configuration import \
    TestConfigurationForMatcher
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check, model_construction
from exactly_lib_test.test_case_utils.string_matcher.test_resources.integration_check import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, expectation_type_config__non_is_success
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class InstructionArgumentsConstructorForExpTypeAndQuantifier:
    """"Constructs instruction arguments for a variant of (expectation type, any-or-every, transformer)."""

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        raise NotImplementedError('abstract method')


class ArgumentsConstructorForPossiblyInvalidSyntax(InstructionArgumentsConstructorForExpTypeAndQuantifier):
    def __init__(self,
                 line_matcher: str,
                 superfluous_args_str: str = '',
                 transformer: str = ''):
        self.transformer = transformer
        self.line_matcher = line_matcher
        self.superfluous_args_str = superfluous_args_str
        self._common_arguments = arguments_building.CommonArgumentsConstructor(transformer)

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
            self._common_arguments,
            arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier, self.line_matcher),
        )

        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str
        return arguments_constructor.apply(expectation_type) + superfluous_args_str


class InstructionArgumentsConstructorForValidSyntax(InstructionArgumentsConstructorForExpTypeAndQuantifier):
    def __init__(self,
                 common_arguments: arguments_building.CommonArgumentsConstructor,
                 line_matcher: str):
        self.common_arguments = common_arguments
        self.line_matcher = line_matcher
        self._common_arguments = common_arguments

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
            self._common_arguments,
            arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier, self.line_matcher),
        )
        return arguments_constructor.apply(expectation_type)


def args_constructor_for(line_matcher: str,
                         transformer: str = '') -> InstructionArgumentsConstructorForExpTypeAndQuantifier:
    return InstructionArgumentsConstructorForValidSyntax(
        arguments_building.CommonArgumentsConstructor(transformer),
        line_matcher)


class TestCaseBase(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.configuration = TestConfigurationForMatcher()

    def shortDescription(self):
        return str(type(self.configuration))

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsConstructorForExpTypeAndQuantifier,
            expected_result_of_positive_test: PassOrFail,
            quantifier: Quantifier,
            actual_file_contents: str,
            symbols: SymbolTable = None,
            expected_symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        for expectation_type in ExpectationType:
            etc = expectation_type_config__non_is_success(expectation_type)
            with self.subTest(expectation_type=expectation_type,
                              quantifier=quantifier.name):

                args_variant = args_variant_constructor.construct(expectation_type,
                                                                  quantifier)
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