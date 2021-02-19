import unittest
from abc import ABC

from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.impls.instructions.multi_phase.timeout.test_resources.abstract_syntax import \
    SYNTAX_ERROR_ARGUMENTS, InstructionArgumentsAbsStx, INVALID_INT_VALUES
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_is
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    is_string_made_up_of_just_strings_reference_restrictions
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx, \
    StringConcatAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf, _CASE_CLASSES)


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType, ABC):
    def __init__(self, conf: ConfigurationBase):
        super().__init__(conf)
        self.conf = conf


class TestInvalidSyntax(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        for invalid_syntax_args in SYNTAX_ERROR_ARGUMENTS:
            with self.subTest(invalid_syntax_args.as_str__default()):
                # ACT & ASSERT #
                self.conf.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
                    self,
                    invalid_syntax_args,
                )


class TestSetValidValue(TestCaseBase):
    def runTest(self):
        # ARRANGE #
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
        # ACT & ASSERT #
        self.conf.instruction_checker.check_parsing__abs_stx__const(
            self,
            self.conf.parser(),
            InstructionArgumentsAbsStx(value_syntax),
            self.conf.arrangement(
                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
            ),
            self.conf.expect_success(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                instruction_settings=asrt_is.matches(
                    timeout=asrt.equals(expected)
                )
            )
        )


class TestInvalidValue(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        for value_case in INVALID_INT_VALUES:
            with self.subTest(value_case):
                # ACT & ASSERT #
                self.conf.instruction_checker.check_parsing__abs_stx__const(
                    self,
                    self.conf.parser(),
                    InstructionArgumentsAbsStx(StringLiteralAbsStx(value_case)),
                    self.conf.arrangement(),
                    self.conf.expect_failing_validation_pre_sds()
                )


_CASE_CLASSES = [
    TestInvalidSyntax,
    TestInvalidValue,
    TestSetValidValue,
]
