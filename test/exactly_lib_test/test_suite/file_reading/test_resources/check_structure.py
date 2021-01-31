import pathlib
import unittest
from pathlib import Path
from typing import List, Sequence

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import Reader
from exactly_lib.test_suite.structure import TestSuiteHierarchy
from exactly_lib_test.processing.test_resources.test_case_processing_assertions import equals_test_case_reference
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, MessageBuilder, \
    AssertionBase
from exactly_lib_test.test_suite.test_resources.environment import default_environment


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
        raise NotImplementedError()


def check(setup: Setup,
          put: unittest.TestCase):
    # ARRANGE #
    with tmp_dir_as_cwd() as tmp_dir_path:
        setup.file_structure_to_read(tmp_dir_path).write_to(tmp_dir_path)
        # ACT #
        actual = Reader(default_environment()).apply(setup.root_suite_based_at(tmp_dir_path))
        # ASSERT #
        expected = setup.expected_structure_based_at(tmp_dir_path)

        expected.apply_without_message(put, actual)


def equals_test_suite(expected: TestSuiteHierarchy) -> Assertion[TestSuiteHierarchy]:
    return matches_test_suite(
        source_file=asrt.equals(expected.source_file),
        file_inclusions_leading_to_this_file=asrt.equals(expected.suite_file_inclusions_leading_to_this_file),
        test_cases=asrt.matches_sequence([
            equals_test_case_reference(test_case)
            for test_case in expected.test_cases
        ]),
        sub_test_suites=asrt.matches_sequence([
            equals_test_suite(sub_test_suite)
            for sub_test_suite in expected.sub_test_suites
        ]),
        test_case_handling_setup=asrt.anything_goes(),
    )


def matches_test_suite(source_file: Assertion[Path],
                       file_inclusions_leading_to_this_file: Assertion[List[Path]],
                       test_case_handling_setup: Assertion[TestCaseHandlingSetup],
                       sub_test_suites: Assertion[Sequence[TestSuiteHierarchy]],
                       test_cases: Assertion[Sequence[TestCaseFileReference]],
                       ) -> Assertion[TestSuiteHierarchy]:
    return MatchesTestSuite(source_file,
                            file_inclusions_leading_to_this_file,
                            test_case_handling_setup,
                            sub_test_suites,
                            test_cases)


class MatchesTestSuite(AssertionBase[TestSuiteHierarchy]):
    def __init__(self,
                 source_file: Assertion[Path],
                 suite_file_inclusions_leading_to_this_file: Assertion[List[Path]],
                 test_case_handling_setup: Assertion[TestCaseHandlingSetup],
                 sub_test_suites: Assertion[Sequence[TestSuiteHierarchy]],
                 test_cases: Assertion[Sequence[TestCaseFileReference]],
                 ):
        self.source_file = source_file
        self.suite_file_inclusions_leading_to_this_file = suite_file_inclusions_leading_to_this_file
        self.test_case_handling_setup = test_case_handling_setup
        self.sub_test_suites = sub_test_suites
        self.test_cases = test_cases

    def _apply(self,
               put: unittest.TestCase,
               value: TestSuiteHierarchy,
               message_builder: MessageBuilder):
        assertion = asrt.and_([
            asrt.sub_component('source_file',
                               TestSuiteHierarchy.source_file.fget,
                               self.source_file),
            asrt.sub_component('suite_file_inclusions_leading_to_this_file',
                               TestSuiteHierarchy.suite_file_inclusions_leading_to_this_file.fget,
                               self.suite_file_inclusions_leading_to_this_file),
            asrt.sub_component('test_case_handling_setup',
                               TestSuiteHierarchy.test_case_handling_setup.fget,
                               self.test_case_handling_setup),
            asrt.sub_component('sub_test_suites',
                               TestSuiteHierarchy.sub_test_suites.fget,
                               self.sub_test_suites),
            asrt.sub_component('test_cases',
                               TestSuiteHierarchy.test_cases.fget,
                               self.test_cases),
        ])
        assertion.apply(put, value, message_builder)
