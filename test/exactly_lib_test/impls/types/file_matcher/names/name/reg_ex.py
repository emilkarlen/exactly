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
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments
from exactly_lib_test.test_resources.matcher_argument import NameRegexComponent
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.regex.test_resources.references import is_reference_to__regex_string_part
from exactly_lib_test.type_val_deps.types.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegExPatternOnBaseName),
        ParseShouldFailWhenRegexArgumentIsMissing(),
        TestWithSymbolReferences(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class TestRegExPatternOnBaseName(test_case_utils.TestCaseBase):
    def test_base_name(self):
        # ARRANGE #
        cases = [
            NEA('exact match',
                True,
                Actual(
                    name_matches_regex_args('name'),
                    pathlib.Path('name'),
                ),
                ),
            NEA('exact match, with ignored dir component',
                True,
                Actual(
                    name_matches_regex_args('base-name'),
                    pathlib.Path('dir-name') / 'base-name',
                ),
                ),
            NEA('exact non-match',
                False,
                Actual(
                    name_matches_regex_args('expected'),
                    pathlib.Path('dir-name') / 'actual',
                ),
                ),
            NEA('pattern 1',
                True,
                Actual(
                    name_matches_regex_args('.*name$'),
                    pathlib.Path('dir-name') / 'file name',
                ),
                ),
            NEA('pattern 2',
                True,
                Actual(
                    name_matches_regex_args('PA..ERN'),
                    pathlib.Path('dir-name') / 'before PATTERN after',
                ),
                ),
            NEA('not match, because pattern with unexpected case is in base name',
                False,
                Actual(
                    name_matches_regex_args('base name'),
                    pathlib.Path('BASE NAME'),
                ),
                ),
            NEA('match, because pattern with unexpected case is in base name, but test is case insensitive',
                True,
                Actual(
                    name_matches_regex_args('base name',
                                            ignore_case=True),
                    pathlib.Path('THE BASE NAME'),
                ),
                ),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)

    def test_fail_when_pattern_matches_dir_components(self):
        # ARRANGE #
        cases = [
            NEA('non-match - name with pattern that matches path components',
                False,
                Actual(
                    name_matches_regex_args('dir-name'),
                    pathlib.Path('dir-name') / pathlib.Path('base-name'),
                ),
                ),
            NEA('non-match - name with pattern that matches path components 2',
                False,
                Actual(
                    name_matches_regex_args('name.*name'),
                    pathlib.Path('dir-name') / pathlib.Path('base-name'),
                ),
                ),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenRegexArgumentIsMissing(test_case_utils.TestCaseBase):
    def runTest(self):
        arguments = arg.Name(arg.NameRegexVariant(
            NameRegexComponent('')
        ))
        self._assert_failing_parse(
            arguments.as_remaining_source
        )


class ValidationShouldFailWhenRegexIsInvalid(test_case_utils.TestCaseBase):
    def runTest(self):
        for regex_case in failing_regex_validation_cases():
            arguments = name_matches_regex_args(regex_case.regex_string)
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
        arguments = name_matches_regex_args('AB' + any_char_regex_string_symbol.name__sym_ref_syntax)
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


def name_matches_regex_args(regex: str,
                            ignore_case: bool = False,
                            ) -> Arguments:
    return arg.Name(
        arg.NameRegexVariant(NameRegexComponent(regex, ignore_case))
    ).as_arguments
