import pathlib
import unittest

from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.file_matcher.test_resources import parse_test_base_classes as test_case_utils
from exactly_lib_test.impls.types.file_matcher.test_resources.test_utils import Actual
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.regex.test_resources.assertions import is_reference_to__regex_string_part
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestGlobPattern(),
        ParseShouldFailWhenPatternArgumentIsMissing(),
        TestWithSymbolReferences(),
    ])


class TestGlobPattern(test_case_utils.TestCaseBase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NEA('exact match, only base name',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('base-name')).as_arguments,
                    pathlib.Path('dir') / 'base-name',
                )),
            NEA('exact match, w dir',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir/base-name')).as_arguments,
                    pathlib.Path('dir') / 'base-name',
                )),
            NEA('glob pattern matching one-and-only component',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('*PATTERN*')).as_arguments,
                    pathlib.Path('before PATTERN after'),
                )),
            NEA('any-string pattern should match',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('*')).as_arguments,
                    pathlib.Path('dir') / 'base-name',
                )),
            NEA('any-string pattern should not stretch over components',
                False,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir*base')).as_arguments,
                    pathlib.Path('dir') / 'base',
                )),
            NEA('not match, because pattern is neither in dir name nor in base name',
                False,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('expected')).as_arguments,
                    pathlib.Path('dir-name') / 'file.txt',
                )),
            NEA('multiple dirs pattern - full match',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir1/*/*.txt')).as_arguments,
                    pathlib.Path('dir1') / 'dir2' / 'file.txt',
                )),
            NEA('multiple dirs pattern - suffix match do match',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir2/*.txt')).as_arguments,
                    pathlib.Path('dir1') / 'dir2' / 'file.txt',
                )),
            NEA('multiple dir pattern - prefix match do not match',
                False,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir1')).as_arguments,
                    pathlib.Path('dir1') / 'dir2' / 'file.txt',
                )),
            NEA('multiple dir pattern - infix match do not match',
                False,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir2')).as_arguments,
                    pathlib.Path('dir1') / 'dir2' / 'file.txt',
                )),
            NEA('pattern with arbitrary dir name',
                True,
                Actual(
                    arg.Path(arg.NameGlobPatternVariant('dir1/*/file.txt')).as_arguments,
                    pathlib.Path('dir1') / 'dir2' / 'file.txt',
                )),
        ]

        # ACT & ASSERT #

        self._check_cases__with_source_variants(cases)


class ParseShouldFailWhenPatternArgumentIsMissing(test_case_utils.TestCaseBase):
    def runTest(self):
        arguments = arg.Path(arg.NameGlobPatternVariant(''))
        self._assert_failing_parse(
            arguments.as_remaining_source
        )


class TestWithSymbolReferences(unittest.TestCase):
    def runTest(self):
        any_char_glob_pattern_string_symbol = StringSymbolContext.of_constant(
            'glob_pattern_string_symbol',
            '*'
        )
        arguments = arg.Path(
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
                        is_reference_to__regex_string_part(any_char_glob_pattern_string_symbol.name),
                    ]),
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(True)
                ),
            )
        )
