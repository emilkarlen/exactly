import types
import unittest

from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches as sut
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail, ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.utils.file_contents.contents_checkers import \
    FilePropertyDescriptorConstructorTestImpl
from exactly_lib_test.instructions.assert_.utils.file_contents.test_resources import \
    destination_file_path_getter_that_gives_seq_of_unique_paths
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_resources.file_utils import tmp_file_containing


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEveryLineMatches),
        unittest.makeSuite(TestAnyLineMatches),
    ])


class Case:
    def __init__(self,
                 name: str,
                 matcher: LineMatcher,
                 expected_result_for_positive_expectation: PassOrFail):
        self.name = name
        self.matcher = matcher
        self.expected_result_for_positive_expectation = expected_result_for_positive_expectation


class TestCaseBase(unittest.TestCase):
    def _check_cases_with_non_empty_file(self,
                                         get_assertion_part_function,
                                         actual_file_contents: str,
                                         matcher_cases: list):

        environment = fake_post_sds_environment()
        checked_file_describer = FilePropertyDescriptorConstructorTestImpl()
        os_services = new_default()

        with destination_file_path_getter_that_gives_seq_of_unique_paths() as dst_file_path_getter:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            with tmp_file_containing(actual_file_contents) as actual_file_path:
                for case in matcher_cases:
                    for expectation_type in ExpectationType:
                        with self.subTest(case=case.name,
                                          expectation_type=expectation_type):
                            ftc = sut.FileToCheck(actual_file_path,
                                                  checked_file_describer,
                                                  environment,
                                                  IdentityLinesTransformer(),
                                                  dst_file_path_getter)
                            matcher_resolver = LineMatcherConstantResolver(case.matcher)
                            assertion_part = get_assertion_part_function(expectation_type,
                                                                         matcher_resolver)
                            # ACT #
                            actual = assertion_part.check_and_return_pfh(environment, os_services, ftc)
                            # ASSERT #
                            pfh_assertion = ExpectationTypeConfig(
                                expectation_type).main_result(case.expected_result_for_positive_expectation)
                            pfh_assertion.apply_without_message(self, actual)

    def _check_cases_for_no_lines(self,
                                  get_assertion_part_function,
                                  expected_result_when_positive_expectation: PassOrFail):
        empty_file_contents = ''
        environment = fake_post_sds_environment()
        checked_file_describer = FilePropertyDescriptorConstructorTestImpl()
        os_services = new_default()

        matchers = [
            ('unconditionally true', LineMatcherConstant(True)),
            ('unconditionally false', LineMatcherConstant(False)),
        ]
        with destination_file_path_getter_that_gives_seq_of_unique_paths() as dst_file_path_getter:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            with tmp_file_containing(empty_file_contents) as actual_file_path:
                for expectation_type in ExpectationType:
                    for matcher_name, matcher in matchers:
                        with self.subTest(expectation_type=expectation_type,
                                          matcher_name=matcher_name):
                            ftc = sut.FileToCheck(actual_file_path,
                                                  checked_file_describer,
                                                  environment,
                                                  IdentityLinesTransformer(),
                                                  dst_file_path_getter)
                            matcher_resolver = LineMatcherConstantResolver(matcher)
                            assertion_part = get_assertion_part_function(expectation_type,
                                                                         matcher_resolver)
                            # ACT #
                            actual = assertion_part.check_and_return_pfh(environment, os_services, ftc)
                            # ASSERT #
                            pfh_assertion = ExpectationTypeConfig(
                                expectation_type).main_result(expected_result_when_positive_expectation)
                            pfh_assertion.apply_without_message(self, actual)


class TestEveryLineMatches(TestCaseBase):
    def test_WHEN_no_lines_THEN_result_SHOULD_be_pass(self):
        self._check_cases_for_no_lines(sut.assertion_part_for_every_line_matches,
                                       PassOrFail.PASS)

    def test_multiple_lines(self):
        file_contents = 'a\nb'

        matcher_cases = [
            Case('matches both lines',
                 matcher=LineMatcherFromPredicates(lambda x: x in (1, 2),
                                                   lambda x: x in ('a', 'b')),
                 expected_result_for_positive_expectation=PassOrFail.PASS),
            Case(
                'matches first line',
                matcher=LineMatcherFromPredicates(lambda x: x == 1,
                                                  lambda x: x in ('a', 'b')),
                expected_result_for_positive_expectation=PassOrFail.FAIL),
        ]

        self._check_cases_with_non_empty_file(sut.assertion_part_for_every_line_matches,
                                              file_contents,
                                              matcher_cases)


class TestAnyLineMatches(TestCaseBase):
    def test_WHEN_no_lines_THEN_result_SHOULD_be_fail(self):
        self._check_cases_for_no_lines(sut.assertion_part_for_any_line_matches,
                                       PassOrFail.FAIL)

    def test_multiple_lines(self):
        file_contents = 'a\nb'

        matcher_cases = [
            Case('matches first line',
                 matcher=is_identical_to(1, 'a'),
                 expected_result_for_positive_expectation=PassOrFail.PASS),
            Case(
                'matches second line',
                matcher=is_identical_to(2, 'b'),
                expected_result_for_positive_expectation=PassOrFail.PASS
            ),
            Case(
                'does not match any line',
                matcher=is_identical_to(1, 'b'),
                expected_result_for_positive_expectation=PassOrFail.FAIL
            ),
        ]

        self._check_cases_with_non_empty_file(sut.assertion_part_for_any_line_matches,
                                              file_contents,
                                              matcher_cases)


def is_identical_to(line_num: int, line_contents: str) -> LineMatcher:
    return LineMatcherFromPredicates(lambda x: x == line_num,
                                     lambda x: x == line_contents)


class LineMatcherFromPredicates(LineMatcher):
    def __init__(self,
                 line_num: types.FunctionType,
                 line_contents: types.FunctionType):
        self.line_num = line_num
        self.line_contents = line_contents

    def matches(self, line: tuple) -> bool:
        return self.line_num(line[0]) and \
               self.line_contents(line[1])

    @property
    def option_description(self) -> str:
        return str(type(self))
