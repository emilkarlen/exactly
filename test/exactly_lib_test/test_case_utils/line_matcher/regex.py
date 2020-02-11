import unittest

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_utils import container, symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as arg
from exactly_lib_test.test_case_utils.line_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.line_matcher.test_resources import test_case_utils
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ExecutionExpectation, \
    ParseExpectation
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.regex.parse_regex import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_case_utils.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, PassOrFail, \
    MAIN_RESULT_ASSERTION__FROM_BOOL
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseAndExecuteValidArguments),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        ValidationShouldFailWhenRegexIsInvalid(),
        TestWithSymbolReferences(),
    ])


class Case:
    def __init__(self,
                 name: str,
                 reg_ex_str: str,
                 line: str,
                 result: bool,
                 ):
        self.name = name
        self.reg_ex_str = reg_ex_str
        self.line = line
        self.result = result


class TestParseAndExecuteValidArguments(unittest.TestCase):
    def runTest(self):
        # Note : NEW LINES are NEVER included in the model
        cases = [
            Case('single character regex that matches',
                 'a',
                 'abc abc',
                 True,
                 ),
            Case('single character regex that not matches',
                 'x',
                 'abc abc',
                 False,
                 ),
            Case('regex that matches',
                 'a..d',
                 '__ abcd __',
                 True,
                 ),
            Case('regex that not matches',
                 'a..d',
                 '__  __',
                 False,
                 ),
        ]
        for case in cases:
            argument_w_opt_neg = arg.WithOptionalNegation(
                arg.Matches(case.reg_ex_str)
            )
            for expectation_type in ExpectationType:
                argument = argument_w_opt_neg.get(expectation_type)
                matcher_arguments = Arguments(str(argument))
                for line_number in (1, 2):
                    model_constructor = integration_check.constant_model((line_number, case.line))
                    with self.subTest(name=case.name,
                                      expectation_type=expectation_type):
                        integration_check.check_with_source_variants(
                            self,
                            matcher_arguments,
                            model_constructor,
                            expectation=Expectation(
                                execution=ExecutionExpectation(
                                    main_result=MAIN_RESULT_ASSERTION__FROM_BOOL[expectation_type][case.result]
                                ),
                            )
                        )


class ParseShouldFailWhenRegexArgumentIsMissing(test_case_utils.TestWithNegationArgumentBase):
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Custom('')
    )

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        self._assert_failing_parse(
            remaining_source(str(self.argument_w_opt_neg.get(maybe_not.expectation_type)))
        )


class ValidationShouldFailWhenRegexIsInvalid(test_case_utils.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        for regex_case in failing_regex_validation_cases():
            argument_w_opt_neg = arg.WithOptionalNegation(
                arg.Matches(regex_case.regex_string)
            )

            with self.subTest(expectation_type=maybe_not.expectation_type,
                              validation_case=regex_case.case_name):
                integration_check.check_with_source_variants(
                    self,
                    arguments=
                    Arguments(str(argument_w_opt_neg.get(maybe_not.expectation_type))),
                    model_constructor=
                    CONSTRUCTOR_OF_ARBITRARY_MODEL,
                    arrangement=
                    symbol_table_from_name_and_sdvs(regex_case.symbols),
                    expectation=
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                        ),
                        ExecutionExpectation(
                            validation=regex_case.expectation
                        ),
                    )
                )


class TestWithSymbolReferences(test_case_utils.TestWithNegationArgumentBase):
    any_char_regex_string_symbol = NameAndValue(
        'valid_regex_string_symbol',
        container(string_sdvs.str_constant('.'))
    )
    argument_w_opt_neg = arg.WithOptionalNegation(
        arg.Matches('AB' + symbol_reference_syntax_for_name(any_char_regex_string_symbol.name))
    )
    matching_model_of_positive_check = (1, 'ABC')

    arrangement = SymbolTable({
        any_char_regex_string_symbol.name: any_char_regex_string_symbol.value,
    })

    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        integration_check.check_with_source_variants(
            self,
            arguments=
            Arguments(str(self.argument_w_opt_neg.get(maybe_not.expectation_type))),
            model_constructor=
            integration_check.constant_model(self.matching_model_of_positive_check),
            arrangement=self.arrangement,
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_valid_regex_string_part(self.any_char_regex_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=maybe_not.main_result(PassOrFail.PASS)
                ),
            )
        )


CONSTRUCTOR_OF_ARBITRARY_MODEL = integration_check.constant_model((1, 'arbitrary line contents'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
