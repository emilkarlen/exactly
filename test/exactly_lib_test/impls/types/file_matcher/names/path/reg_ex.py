import pathlib
import unittest

from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.impls.types.file_matcher.test_resources.integration_check import ARBITRARY_MODEL
from exactly_lib_test.impls.types.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.matcher_argument import NameRegexComponent
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.regex.test_resources.references import is_reference_to__regex_string_part
from exactly_lib_test.type_val_deps.types.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegExPatternOnWholePath),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        TestWithSymbolReferences(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class TestRegExPatternOnWholePath(test_case_utils.TestCaseBase):
    def test_whole_path(self):
        # ARRANGE #
        cases = [
            NEA('exact match in base name',
                True,
                Actual(
                    path_matches_regex_args('base-name'),
                    pathlib.Path('dir-name') / 'base-name',
                ),
                ),
            NEA('exact match in dir name',
                True,
                Actual(
                    path_matches_regex_args('dir-name'),
                    pathlib.Path('dir-name') / 'base-name',
                ),
                ),
            NEA('exact non-match',
                False,
                Actual(
                    path_matches_regex_args('expected'),
                    pathlib.Path('dir-name') / 'actual',
                ),
                ),
            NEA('pattern 1',
                True,
                Actual(
                    path_matches_regex_args('.*name$'),
                    pathlib.Path('dir-name') / 'file name',
                ),
                ),
            NEA('pattern 2 (in dir component)',
                True,
                Actual(
                    path_matches_regex_args('PA..ERN'),
                    pathlib.Path('before PATTERN after') / 'base-name',
                ),
                ),
            NEA('pattern stretching over dir component and base name',
                True,
                Actual(
                    path_matches_regex_args('component.*name'),
                    pathlib.Path('dir-component') / 'base-name',
                ),
                ),
            NEA('not match, because unexpected case',
                False,
                Actual(
                    path_matches_regex_args('base name'),
                    pathlib.Path('BASE NAME'),
                ),
                ),
            NEA('match, because pattern with unexpected case exists, but test is case insensitive',
                True,
                Actual(
                    path_matches_regex_args('dir.*base',
                                            ignore_case=True),
                    pathlib.Path('dir-component') / 'base-name',
                ),
                ),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)

    def test_fail_when_pattern_matches_base_name(self):
        # ARRANGE #
        cases = [
            NEA('non-match - pattern matches on base name only',
                False,
                Actual(
                    path_matches_regex_args('^base-name'),
                    pathlib.Path('dir-name') / pathlib.Path('base-name'),
                ),
                ),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenRegexArgumentIsMissing(test_case_utils.TestCaseBase):
    def runTest(self):
        arguments = arg.Path(arg.NameRegexVariant(
            NameRegexComponent('')
        ))
        self._assert_failing_parse(
            arguments.as_remaining_source
        )


class ValidationShouldFailWhenRegexIsInvalid(test_case_utils.TestCaseBase):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            arguments = path_matches_regex_args(regex_case.regex_string)
            for expectation_type in ExpectationType:
                with self.subTest(expectation_type=expectation_type,
                                  validation_case=regex_case.case_name):
                    self._check_with_source_variants(
                        arguments=
                        arguments,
                        model_constructor=
                        ARBITRARY_MODEL,
                        arrangement=
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(regex_case.symbols)
                        ),
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


class TestWithSymbolReferences(test_case_utils.TestCaseBase):
    def runTest(self):
        any_char_regex_string_symbol = StringSymbolContext.of_constant(
            'valid_regex_string_symbol',
            '.',
        )
        arguments = path_matches_regex_args('AB' + any_char_regex_string_symbol.name__sym_ref_syntax)
        self._check_with_source_variants(
            arguments=
            arguments,
            model_constructor=
            integration_check.constant_relative_file_name('ABC'),
            arrangement=arrangement_w_tcds(
                symbols=any_char_regex_string_symbol.symbol_table
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to__regex_string_part(any_char_regex_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            )
        )


def path_matches_regex_args(regex: str,
                            ignore_case: bool = False,
                            ) -> Arguments:
    return arg.Path(
        arg.NameRegexVariant(NameRegexComponent(regex, ignore_case))
    ).as_arguments
