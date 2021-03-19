import unittest

from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration, TestWithConfigurationBase
from exactly_lib_test.symbol.test_resources.symbol_syntax import \
    NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.symbol_context import \
    StringMatcherSymbolContext


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString(configuration),
        ParseShouldFailWhenCheckIsMissing(configuration),
        ParseShouldFailWhenCheckIsIllegal(configuration),
    ])


class ParseShouldFailWhenActualIsFollowedByIllegalOptionOrString(TestWithConfigurationBase):
    def runTest(self):
        # ARRANGE #
        string_matcher__const_true = StringMatcherSymbolContext.of_primitive_constant('STRING_MATCHER', True)
        cases = [
            NameAndValue('illegal option',
                         option_syntax.long_option_syntax('this-is-an-illegal-option')),
            NameAndValue('illegal argument',
                         'this-is-an-illegal-argument'),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                # ACT & ASSERT #
                self.configuration.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
                    self,
                    self.configuration.syntax_for_matcher(
                        SequenceAbsStx.preceded_by_str(
                            case.value,
                            self.configuration.syntax_for_matcher(string_matcher__const_true.abstract_syntax),
                        )
                    )
                )


class ParseShouldFailWhenCheckIsMissing(TestWithConfigurationBase):
    def runTest(self):
        # ACT & ASSERT #
        self.configuration.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
            self,
            self.configuration.syntax_for_matcher(
                self.configuration.syntax_for_matcher(
                    CustomAbsStx.empty()
                )
            )
        )


class ParseShouldFailWhenCheckIsIllegal(TestWithConfigurationBase):
    def runTest(self):
        # ACT & ASSERT #
        self.configuration.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
            self,
            self.configuration.syntax_for_matcher(
                CustomAbsStx.of_str(NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME)
            )
        )
