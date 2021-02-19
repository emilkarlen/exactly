import unittest

from exactly_lib.impls.instructions.multi_phase.timeout import doc
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.timeout.test_resources.abstract_syntax import \
    InstructionArgumentsAbsStx, SYNTAX_ERROR_ARGUMENTS, INVALID_INT_VALUES
from exactly_lib_test.impls.instructions.multi_phase.timeout.test_resources.instruction_check import PARSE_CHECKER, \
    CHECKER
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_instr_settings
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    is_string_made_up_of_just_strings_reference_restrictions
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx, \
    StringConcatAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParse(),
        TestInvalidValue(),
        TestValidValue(),
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
                InstructionArgumentsAbsStx(StringLiteralAbsStx(value_case)),
                embryo_check.Arrangement.phase_agnostic(),
                embryo_check.MultiSourceExpectation.phase_agnostic(
                    validation=ValidationAssertions.pre_sds_fails__w_any_msg()
                ),
                value_case=value_case,
            )


class TestValidValue(unittest.TestCase):
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
                    InstructionArgumentsAbsStx(case.input_value),
                    embryo_check.Arrangement.phase_agnostic(),
                    embryo_check.MultiSourceExpectation.phase_agnostic(
                        instruction_settings=asrt_instr_settings.matches(
                            timeout=asrt.equals(case.expected_value)
                        )
                    ),
                )


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        string_72_plus = StringSymbolContext.of_constant(
            'SYMBOL_72_PLUS',
            '72+',
            default_restrictions=is_string_made_up_of_just_strings_reference_restrictions(),
        )
        string_5 = StringSymbolContext.of_constant(
            'SYMBOL_5',
            '5',
            default_restrictions=is_string_made_up_of_just_strings_reference_restrictions(),
        )
        expected = 72 + 5

        all_symbols = [string_72_plus, string_5]

        value_syntax = StringConcatAbsStx([
            string_72_plus.abstract_syntax,
            string_5.abstract_syntax,
        ])
        CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            InstructionArgumentsAbsStx(value_syntax),
            embryo_check.Arrangement.phase_agnostic(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
            ),
            embryo_check.MultiSourceExpectation.phase_agnostic(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                instruction_settings=asrt_instr_settings.matches(
                    timeout=asrt.equals(expected)
                )
            ),
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
