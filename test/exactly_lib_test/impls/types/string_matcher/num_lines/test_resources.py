import unittest
from typing import Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.impls.types.string_matcher.test_resources import integration_check, test_configuration
from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.impls.types.string_models.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    PassOrFail, expectation_type_config__non_is_success
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    nothing__if_positive__not_option__if_negative
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
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
            transformation = ' '.join([
                option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                self.transformer
            ])

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
    def _check(
            self,
            source: ParseSource,
            model: ModelConstructor,
            arrangement: Arrangement,
            expectation: Expectation):

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            source,
            model,
            arrangement,
            expectation,
        )

    def _check_single_expression_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expectation_type: ExpectationType,
            model: ModelConstructor,
            arrangement: Arrangement,
            expectation: Expectation):

        args_variant = args_variant_constructor.construct(expectation_type)
        complete_instruction_arguments = test_configuration.arguments_for(args_variant)

        for source in equivalent_source_variants__with_source_check__for_expression_parser(
                self,
                complete_instruction_arguments):
            integration_check.CHECKER__PARSE_FULL.check(
                self,
                source,
                model,
                arrangement,
                expectation,
            )

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expected_result_of_positive_test: PassOrFail,
            actual_file_contents: str,
            symbols: SymbolTable = None,
            expected_symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence):
        for expectation_type in ExpectationType:
            etc = expectation_type_config__non_is_success(expectation_type)
            with self.subTest(expectation_type=expectation_type):

                args_variant = args_variant_constructor.construct(expectation_type)
                complete_instruction_arguments = test_configuration.arguments_for(args_variant)

                for source in equivalent_source_variants__with_source_check__for_expression_parser(
                        self,
                        complete_instruction_arguments):
                    integration_check.CHECKER__PARSE_FULL.check(
                        self,
                        source,
                        model_constructor.of_str(self, actual_file_contents),
                        Arrangement(
                            tcds=TcdsArrangement(
                                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
                            ),
                            symbols=symbols),
                        Expectation(
                            ParseExpectation(
                                symbol_references=expected_symbol_references,
                            ),
                            ExecutionExpectation(
                                main_result=etc.main_result(expected_result_of_positive_test),
                            ),
                        )
                    )
