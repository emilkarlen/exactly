import unittest

from exactly_lib.impls.instructions.multi_phase.timeout import doc
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    MultiSourceExpectation
from exactly_lib_test.impls.instructions.multi_phase.timeout.test_resources.abstract_syntax import \
    InstructionArgumentsAbsStx, SYNTAX_ERROR_ARGUMENTS, INVALID_INT_VALUES
from exactly_lib_test.impls.instructions.multi_phase.timeout.test_resources.instruction_check import PARSE_CHECKER, \
    CHECKER
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_data_rest
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx, \
    StringConcatAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParse(),
        TestInvalidValue(),
        TestValidIntValue(),
        TestNone(),
        TestSymbolReferences(),
        suite_for_instruction_documentation(doc.TheInstructionDocumentation('instruction name')),
    ])


class TestFailingParse(unittest.TestCase):
    def runTest(self):
        for syntax in SYNTAX_ERROR_ARGUMENTS:
            with self.subTest(syntax.as_str__default()):
                PARSE_CHECKER.check_invalid_syntax__src_var_consume_last_line_abs_stx(
                    self,
                    syntax,
                )


class TestInvalidValue(unittest.TestCase):
    def runTest(self):
        for value_case in INVALID_INT_VALUES:
            CHECKER.check__abs_stx__layout_and_source_variants(
                self,
                InstructionArgumentsAbsStx.of_int(StringLiteralAbsStx(value_case)),
                Arrangement.phase_agnostic(),
                MultiSourceExpectation.phase_agnostic(
                    validation=ValidationAssertions.pre_sds_fails__w_any_msg()
                ),
                sub_test_identifiers={'value_case': value_case},
            )


class TestValidIntValue(unittest.TestCase):
    def runTest(self):
        cases = [
            NIE('constant 5',
                5,
                StringLiteralAbsStx('5'),
                ),
            NIE('constant 5 / quoted',
                5,
                StringLiteralAbsStx('5', QuoteType.SOFT),
                ),
            NIE('constant 75',
                75,
                StringLiteralAbsStx('75'),
                ),
            NIE('python expr',
                5,
                StringLiteralAbsStx('2+3'),
                ),
            NIE('python expr with space',
                7,
                StringLiteralAbsStx('2*3 + 1', QuoteType.HARD),
                ),
            NIE('python expr len',
                11,
                StringLiteralAbsStx('len("hello world")', QuoteType.HARD),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                CHECKER.check__abs_stx__layout_and_source_variants(
                    self,
                    InstructionArgumentsAbsStx.of_int(case.input_value),
                    Arrangement.phase_agnostic(),
                    MultiSourceExpectation.phase_agnostic(
                        instruction_settings=asrt_instr_settings.matches(
                            timeout=asrt.equals(case.expected_value)
                        )
                    ),
                )


class TestNone(unittest.TestCase):
    def runTest(self):
        CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            InstructionArgumentsAbsStx.of_none(),
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                instruction_settings=asrt_instr_settings.matches(
                    timeout=asrt.is_none
                )
            ),
        )


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        string_72_plus = StringSymbolContext.of_constant(
            'SYMBOL_72_PLUS',
            '72+',
            default_restrictions=asrt_data_rest.is__string__w_all_indirect_refs_are_strings(),
        )
        string_5 = StringSymbolContext.of_constant(
            'SYMBOL_5',
            '5',
            default_restrictions=asrt_data_rest.is__string__w_all_indirect_refs_are_strings(),
        )
        expected = 72 + 5

        all_symbols = [string_72_plus, string_5]

        value_syntax = StringConcatAbsStx([
            string_72_plus.abstract_syntax,
            string_5.abstract_syntax,
        ])
        CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            InstructionArgumentsAbsStx.of_int(value_syntax),
            Arrangement.phase_agnostic(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
            ),
            MultiSourceExpectation.phase_agnostic(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                instruction_settings=asrt_instr_settings.matches(
                    timeout=asrt.equals(expected)
                )
            ),
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
