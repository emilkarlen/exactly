import pathlib
import unittest

from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.impls.types.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.regex.test_resources.assertions import is_reference_to_valid_regex_string_part
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestGlobPattern),
        ParseShouldFailWhenPatternArgumentIsMissing(),
        TestWithSymbolReferences(),
    ])


class TestGlobPattern(test_case_utils.TestCaseBase):
    def test_base_name(self):
        # ARRANGE #
        cases = [
            NEA('exact match',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('pattern')).as_arguments,
                    pathlib.Path('pattern'),
                )),
            NEA('exact match - with ignored dir component',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('base-name')).as_arguments,
                    pathlib.Path('dir') / 'base-name',
                )),
            NEA('any-string pattern matching the whole name',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('*PATTERN*')).as_arguments,
                    pathlib.Path('before PATTERN after'),
                )),
            NEA('character set',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('[123]x')).as_arguments,
                    pathlib.Path('1x'),
                )),
            NEA('negated character set',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('[!123]x')).as_arguments,
                    pathlib.Path('ax'),
                )),
            NEA('character range',
                True,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('[1-3]x')).as_arguments,
                    pathlib.Path('2x'),
                )),
            NEA('pattern matching the end of the name',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('end')).as_arguments,
                    pathlib.Path('start middle end'),
                )),
            NEA('pattern matching the start of the name',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('start')).as_arguments,
                    pathlib.Path('start middle end'),
                )),
            NEA('pattern matching the start of the name',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('middle')).as_arguments,
                    pathlib.Path('start middle end'),
                )),
            NEA('not match, because pattern is not in base name',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('expected')).as_arguments,
                    pathlib.Path('actual'),
                )),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)

    def test_fail_when_pattern_matches_dir_components(self):
        # ARRANGE #
        cases = [
            NEA('pattern that matches path components',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('dir-name/*.txt')).as_arguments,
                    pathlib.Path('dir-name') / 'file.txt',
                )),
            NEA('pattern with zero-or-more-dirs pattern',
                False,
                Actual(
                    arg.Name(arg.NameGlobPatternVariant('**/*.txt')).as_arguments,
                    pathlib.Path('dir-name') / 'file.txt',
                )),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenPatternArgumentIsMissing(test_case_utils.TestCaseBase):
    def runTest(self):
        arguments = arg.Name(arg.NameGlobPatternVariant(''))
        self._assert_failing_parse(
            arguments.as_remaining_source
        )


class TestWithSymbolReferences(unittest.TestCase):
    def runTest(self):
        any_char_glob_pattern_string_symbol = StringSymbolContext.of_constant(
            'glob_pattern_string_symbol',
            '*'
        )
        arguments = arg.Name(
            arg.NameGlobPatternVariant('AB' + any_char_glob_pattern_string_symbol.name__sym_ref_syntax))

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            arguments=
            arguments.as_arguments,
            input_=
            integration_check.constant_relative_file_name('ABC'),
            arrangement=arrangement_w_tcds(
                symbols=any_char_glob_pattern_string_symbol.symbol_table
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        is_reference_to_valid_regex_string_part(any_char_glob_pattern_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            )
        )
