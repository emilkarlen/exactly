import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_utils.test_resources import svh_assertions as svh_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def int_condition(operator: comparators.ComparisonOperator,
                  value: int) -> str:
    return operator.name + ' ' + str(value)


class InstructionArgumentsVariantConstructor:
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        raise NotImplementedError('abstract method')


class Configuration:
    def __init__(self,
                 parser: InstructionParser,
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
               arrangement: ArrangementPostAct,
               expectation: Expectation
               ):
        instruction_check.check(self,
                                self._conf().parser,
                                source,
                                arrangement,
                                expectation)

    def test_invalid_integer_argument_according_to_custom_validation(self):
        for invalid_integer_value in self._conf().invalid_integers_according_to_custom_validation:
            with self.subTest(invalid_integer_value=str(invalid_integer_value)):
                condition_str = int_condition(comparators.EQ, invalid_integer_value)
                instr_arg = self._conf().arguments_constructor.apply(condition_str)
                for source in equivalent_source_variants__with_source_check(self, instr_arg):
                    self._check(
                        source,
                        ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=svh_asrt.is_validation_error(),
                            symbol_usages=asrt.is_empty_list,
                        ),
                    )

    def test_invalid_arguments_without_symbol_references(self):
        test_cases = [
            ' = a',
            '> 1.5',
        ]
        for condition_str in test_cases:
            with self.subTest(msg=condition_str):
                instr_arg = self._conf().arguments_constructor.apply(condition_str)
                for source in equivalent_source_variants__with_source_check(self, instr_arg):
                    self._check(
                        source,
                        ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=svh_asrt.is_validation_error(),
                            symbol_usages=asrt.is_empty_list,
                        ),
                    )

    def test_invalid_arguments_with_symbol_references(self):
        symbol = SymbolWithReferenceSyntax('symbol_name')
        operand_arg_with_symbol_ref_list = [
            ' = {}'.format(symbol),
        ]
        invalid_symbol_values = [
            'not_a_number',
            '1.5',
            '72 87',
        ]
        for invalid_symbol_value in invalid_symbol_values:
            for operand_arg_with_symbol_ref in operand_arg_with_symbol_ref_list:
                arguments = self._conf().arguments_constructor.apply(operand_arg_with_symbol_ref)
                with self.subTest(argument=arguments,
                                  invalid_symbol_value=invalid_symbol_value):
                    for source in equivalent_source_variants__with_source_check(self, arguments):
                        self._check(
                            source,
                            ArrangementPostAct(
                                symbols=SymbolTable({
                                    symbol.name: data_symbol_utils.string_constant_container(
                                        invalid_symbol_value
                                    )
                                })
                            ),
                            Expectation(
                                validation_pre_sds=svh_asrt.is_validation_error(),
                                symbol_usages=equals_symbol_references([
                                    SymbolReference(symbol.name,
                                                    string_made_up_by_just_strings())
                                ]),
                            ),
                        )
