import unittest
from typing import Callable, Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case_utils.matcher.impls import sdv_components, combinator_sdvs
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.test_case_utils.os_services.os_services_access import new_for_current_os
from exactly_lib.test_case_utils.string_matcher.impl import line_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib_test.instructions.assert_.utils.file_contents.test_resources import \
    string_model_factory
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, pfh_expectation_type_config
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing
from exactly_lib_test.type_system.logic.test_resources.values import is_identical_to, line_matcher_from_predicates


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
    def _check_cases_with_non_empty_file(
            self,
            get_assertion_part_function: Callable[[ExpectationType, LineMatcherSdv], FileContentsAssertionPart],
            actual_file_contents: str,
            matcher_cases: Sequence[Case]):

        environment = fake_post_sds_environment()
        os_services = new_for_current_os()

        with string_model_factory() as model_factory:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            with tmp_file_containing(actual_file_contents) as actual_file_path:
                for case in matcher_cases:
                    for expectation_type in ExpectationType:
                        with self.subTest(case=case.name,
                                          expectation_type=expectation_type):
                            model = model_factory.of_file(actual_file_path)
                            matcher_sdv = sdv_components.matcher_sdv_from_constant_primitive(case.matcher)
                            assertion_part = get_assertion_part_function(expectation_type,
                                                                         matcher_sdv)
                            # ACT #
                            actual = assertion_part.check_and_return_pfh(environment, os_services, model)
                            # ASSERT #
                            pfh_assertion = pfh_expectation_type_config(
                                expectation_type).main_result(case.expected_result_for_positive_expectation)
                            pfh_assertion.apply_without_message(self, actual)

    def _check_cases_for_no_lines(
            self,
            get_assertion_part_function:
            Callable[[ExpectationType, LineMatcherSdv], AssertionPart[StringModel, pfh.PassOrFailOrHardError]],
            expected_result_when_positive_expectation: PassOrFail):
        empty_file_contents = ''
        environment = fake_post_sds_environment()
        os_services = new_for_current_os()

        matchers = [
            ('unconditionally true', MatcherWithConstantResult(True)),
            ('unconditionally false', MatcherWithConstantResult(False)),
        ]
        with string_model_factory() as model_factory:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            with tmp_file_containing(empty_file_contents) as actual_file_path:
                for expectation_type in ExpectationType:
                    for matcher_name, matcher in matchers:
                        with self.subTest(expectation_type=expectation_type,
                                          matcher_name=matcher_name):
                            model = model_factory.of_file(actual_file_path)
                            matcher_sdv = sdv_components.matcher_sdv_from_constant_primitive(matcher)
                            assertion_part = get_assertion_part_function(expectation_type,
                                                                         matcher_sdv)
                            # ACT #
                            actual = assertion_part.check_and_return_pfh(environment, os_services, model)
                            # ASSERT #
                            pfh_assertion = pfh_expectation_type_config(
                                expectation_type).main_result(expected_result_when_positive_expectation)
                            pfh_assertion.apply_without_message(self, actual)


class TestEveryLineMatches(TestCaseBase):
    def test_WHEN_no_lines_THEN_result_SHOULD_be_pass(self):
        self._check_cases_for_no_lines(assertion_part_for_every_line_matches,
                                       PassOrFail.PASS)

    def test_multiple_lines(self):
        file_contents = 'a\nb'

        matcher_cases = [
            Case('matches both lines',
                 matcher=line_matcher_from_predicates(lambda x: x in (1, 2),
                                                      lambda x: x in ('a', 'b')),
                 expected_result_for_positive_expectation=PassOrFail.PASS),
            Case(
                'matches first line',
                matcher=line_matcher_from_predicates(lambda x: x == 1,
                                                     lambda x: x in ('a', 'b')),
                expected_result_for_positive_expectation=PassOrFail.FAIL),
        ]

        self._check_cases_with_non_empty_file(assertion_part_for_every_line_matches,
                                              file_contents,
                                              matcher_cases)


class TestAnyLineMatches(TestCaseBase):
    def test_WHEN_no_lines_THEN_result_SHOULD_be_fail(self):
        self._check_cases_for_no_lines(assertion_part_for_any_line_matches,
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

        self._check_cases_with_non_empty_file(assertion_part_for_any_line_matches,
                                              file_contents,
                                              matcher_cases)


def assertion_part_for_every_line_matches(expectation_type: ExpectationType,
                                          line_matcher_sdv: LineMatcherSdv) -> FileContentsAssertionPart:
    return StringMatcherAssertionPart(
        sdv__of_expectation_type(expectation_type, Quantifier.ALL, line_matcher_sdv)
    )


def assertion_part_for_any_line_matches(expectation_type: ExpectationType,
                                        line_matcher_sdv: LineMatcherSdv) -> FileContentsAssertionPart:
    return StringMatcherAssertionPart(
        sdv__of_expectation_type(expectation_type, Quantifier.EXISTS, line_matcher_sdv)
    )


def sdv__of_expectation_type(expectation_type: ExpectationType,
                             quantifier: Quantifier,
                             line_matcher_sdv: LineMatcherSdv) -> StringMatcherSdv:
    return combinator_sdvs.new_maybe_negated(
        line_matchers.sdv(quantifier, line_matcher_sdv),
        expectation_type,
    )
