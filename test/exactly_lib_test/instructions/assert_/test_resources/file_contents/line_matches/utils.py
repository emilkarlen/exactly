import unittest

from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.test_case_utils.string_matcher.quant_over_lines.test_resources import \
    InstructionArgumentsConstructorForExpTypeAndQuantifier
from exactly_lib_test.test_case_utils.string_matcher.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, pfh_expectation_type_config
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class TestCaseBase(unittest.TestCase):
    def __init__(self, configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

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
            etc = pfh_expectation_type_config(expectation_type)
            with self.subTest(expectation_type=expectation_type,
                              quantifier=quantifier.name):

                args_variant = args_variant_constructor.construct(expectation_type,
                                                                  quantifier)
                complete_instruction_arguments = self.configuration.arguments_for(args_variant)

                for source in equivalent_source_variants__with_source_check__multi_line(self,
                                                                                        complete_instruction_arguments):
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
