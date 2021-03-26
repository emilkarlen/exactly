import unittest
from typing import Sequence

from exactly_lib.impls.types.integer import parse_integer as sut
from exactly_lib.impls.types.integer.integer_ddv import IntegerDdv
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib_test.impls.types.integer.test_resources.case_setup import Symbol, Case, Expected
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_hds, fake_sds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.value_assertions.value_assertion import AssertionBase, MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import parse_from_tokens_checker
from exactly_lib_test.type_val_deps.dep_variants.test_resources.parse_from_tokens_checker import Expectation
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    equals_symbol_references__w_str_rendering
from exactly_lib_test.type_val_deps.types.integer.test_resources.abstract_syntax import IntegerAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidateAndResolveViaParseChecker(),
    ])


class TestValidateAndResolveViaParseChecker(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        symbol_simple = Symbol('symbol_simple', 3, '3')

        symbol_complex = Symbol('symbol_complex', 7, '2 + 5')

        defined_symbols = self._symbol_table_with_string_values([
            symbol_simple,
            symbol_complex,
        ])

        the_instruction_environment = InstructionEnvironmentPostSdsBuilder.new(
            hds=fake_hds(),
            environ={},
            sds=fake_sds(),
            symbols=defined_symbols,
        ).build_post_sds()

        cases = [
            Case(
                'single constant integer',
                '1',
                Expected(
                    resolved_value=1,
                    symbol_references=[])
            ),
            Case(
                'single symbol reference with simple contents',
                symbol_simple.ref_syntax,
                Expected(
                    resolved_value=symbol_simple.value_int,
                    symbol_references=[symbol_simple.symbol_reference]
                )),
            Case(
                'constant complex expression',
                surrounded_by_soft_quotes_str('1 + 2 * 3 * (2+2)'),
                Expected(
                    resolved_value=1 + 2 * 3 * (2 + 2),
                    symbol_references=[])
            ),
            Case(
                'single symbol reference with complex contents',
                symbol_complex.ref_syntax,
                Expected(
                    resolved_value=symbol_complex.value_int,
                    symbol_references=[symbol_complex.symbol_reference]
                )
            ),
            Case(
                'mixed expression',
                surrounded_by_soft_quotes_str(
                    '1 + {symbol_simple} * ({symbol_complex})'.format(
                        symbol_simple=symbol_simple.ref_syntax,
                        symbol_complex=symbol_complex.ref_syntax)
                ),
                Expected(
                    resolved_value=1 + symbol_simple.value_int * symbol_complex.value_int,
                    symbol_references=[symbol_simple.symbol_reference,
                                       symbol_complex.symbol_reference]
                )
            ),
        ]
        environment = the_instruction_environment.path_resolving_environment_pre_or_post_sds
        for case in cases:
            syntax = IntegerAbsStx(
                StringLiteralAbsStx(case.source)
            )
            CHECKER.check__abs_stx__expr_parse_source_variants(
                self,
                syntax,
                defined_symbols,
                expectation=Expectation(
                    symbol_references=equals_symbol_references__w_str_rendering(case.expected.symbol_references),
                    sdv=ValidationAssertion(environment),
                    ddv=_DDvAssertion(environment, case.expected.resolved_value),
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )

    @staticmethod
    def _symbol_table_with_string_values(all_symbols: Sequence[Symbol]):
        return SymbolContext.symbol_table_of_contexts([
            StringConstantSymbolContext(sym.name, sym.value_str)
            for sym in all_symbols
        ])


class ValidationAssertion(AssertionBase[sut.IntegerSdv]):
    def __init__(self, environment: PathResolvingEnvironmentPreSds):
        self._environment = environment

    def _apply(self,
               put: unittest.TestCase,
               value: sut.IntegerSdv,
               message_builder: MessageBuilder,
               ):
        value.validate_pre_sds(self._environment)


class _DDvAssertion(AssertionBase[IntegerDdv]):
    def __init__(self,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 expected_resolved_value: int,
                 ):
        self._environment = environment
        self._expected_resolved_value = expected_resolved_value

    def _apply(self,
               put: unittest.TestCase,
               value: IntegerDdv,
               message_builder: MessageBuilder,
               ):
        actual = value.value_of_any_dependency(self._environment.tcds)
        put.assertEqual(self._expected_resolved_value,
                        actual,
                        message_builder.apply('int value'))


CHECKER = parse_from_tokens_checker.Checker(sut.MandatoryIntegerParser())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
