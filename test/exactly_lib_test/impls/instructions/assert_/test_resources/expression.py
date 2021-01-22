import unittest

from exactly_lib.impls.types.condition import comparators
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_case.result.test_resources import svh_assertions as svh_asrt
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


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

    def test_invalid_arguments_without_symbol_references(self):
        test_cases = [
            ' {op} a'.format(op=comparators.EQ.name),
            '{op} 1.5'.format(op=comparators.GT.name),
        ]
        for condition_str in test_cases:
            with self.subTest(msg=condition_str):
                instr_arg = self._conf().arguments_constructor.apply(condition_str)
                for source in equivalent_source_variants__with_source_check__consume_last_line(self, instr_arg):
                    self._check(
                        source,
                        ArrangementPostAct(),
                        Expectation(
                            validation_pre_sds=svh_asrt.is_validation_error(),
                            symbol_usages=asrt.is_empty_sequence,
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
                    for source in equivalent_source_variants__with_source_check__consume_last_line(self, arguments):
                        self._check(
                            source,
                            ArrangementPostAct(
                                symbols=symbol.symbol_table
                            ),
                            Expectation(
                                validation_pre_sds=svh_asrt.is_validation_error(),
                                symbol_usages=asrt.matches_sequence([
                                    symbol.reference_assertion__string_made_up_of_just_strings
                                ]),
                            ),
                        )