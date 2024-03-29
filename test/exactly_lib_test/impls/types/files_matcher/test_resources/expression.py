import unittest

from exactly_lib.impls.types.condition import comparators
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib_test.impls.types.files_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.files_matcher.test_resources import model
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expression_parser
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.validation import validation as asrt_validation
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


class InstructionArgumentsVariantConstructor:
    """
    Constructs the instruction argument for a given comparison condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        raise NotImplementedError('abstract method')


class Configuration:
    def __init__(self,
                 parser: Parser[FilesMatcherSdv],
                 arguments_constructor: InstructionArgumentsVariantConstructor,
                 invalid_integers_according_to_custom_validation: list):
        self.parser = parser
        self.arguments_constructor = arguments_constructor
        self.invalid_integers_according_to_custom_validation = invalid_integers_according_to_custom_validation


class TestFailingValidationPreSdsAbstract(unittest.TestCase):
    def _conf(self) -> Configuration:
        raise NotImplementedError('abstract method')

    def _check(self,
               source: ParseSource,
               arrangement: Arrangement,
               expectation: Expectation,
               ):
        integration_check.CHECKER__PARSE_FULL.check(self,
                                                    source,
                                                    model.arbitrary_model(),
                                                    arrangement,
                                                    expectation)

    def test_invalid_arguments_without_symbol_references(self):
        test_cases = [
            ' {op} a'.format(op=comparators.EQ.name),
            '{op} 1.5'.format(op=comparators.GT.name),
        ]
        for condition_str in test_cases:
            with self.subTest(msg=condition_str):
                instr_arg = self._conf().arguments_constructor.apply(condition_str)
                for source in equivalent_source_variants__for_expression_parser(
                        self,
                        Arguments(instr_arg)):
                    self._check(
                        source,
                        Arrangement(),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.is_empty_sequence,
                            ),
                            ExecutionExpectation(
                                validation=asrt_validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                            ),
                        ),
                    )

    def test_invalid_arguments_with_symbol_references(self):
        symbol_name = SymbolWithReferenceSyntax('symbol_name')
        operand_arg_with_symbol_ref_list = [
            ' {op} {sym}'.format(op=comparators.EQ.name,
                                 sym=symbol_name),
        ]
        invalid_symbol_values = [
            'not_a_number',
            '1.5',
            '72 87',
        ]
        for invalid_symbol_value in invalid_symbol_values:
            symbol = StringConstantSymbolContext(symbol_name.name, invalid_symbol_value)
            for operand_arg_with_symbol_ref in operand_arg_with_symbol_ref_list:
                arguments = self._conf().arguments_constructor.apply(operand_arg_with_symbol_ref)
                with self.subTest(argument=arguments,
                                  invalid_symbol_value=invalid_symbol_value):
                    for source in equivalent_source_variants__for_expression_parser(
                            self,
                            Arguments(arguments)):
                        self._check(
                            source,
                            Arrangement(
                                symbols=symbol.symbol_table
                            ),
                            Expectation(
                                ParseExpectation(
                                    symbol_references=asrt.matches_sequence([
                                        symbol.reference_assertion__string__w_all_indirect_refs_are_strings
                                    ]),
                                ),
                                ExecutionExpectation(
                                    validation=asrt_validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                                ),
                            ),
                        )
