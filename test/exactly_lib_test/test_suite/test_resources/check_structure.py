import pathlib
import unittest
from pathlib import Path
from typing import List, Sequence

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import Reader
from exactly_lib_test.processing.test_resources.test_case_processing_assertions import equals_test_case_reference
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder, \
    ValueAssertionBase
from exactly_lib_test.test_suite.test_resources.environment import default_environment


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
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


def equals_test_suite(expected: structure.TestSuite) -> ValueAssertion[structure.TestSuite]:
    return matches_test_suite(
        source_file=asrt.equals(expected.source_file),
        file_inclusions_leading_to_this_file=asrt.equals(expected.file_inclusions_leading_to_this_file),
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


def matches_test_suite(source_file: ValueAssertion[Path],
                       file_inclusions_leading_to_this_file: ValueAssertion[List[Path]],
                       test_case_handling_setup: ValueAssertion[TestCaseHandlingSetup],
                       sub_test_suites: ValueAssertion[Sequence[structure.TestSuite]],
                       test_cases: ValueAssertion[Sequence[TestCaseFileReference]],
                       ) -> ValueAssertion[structure.TestSuite]:
    return MatchesTestSuite(source_file,
                            file_inclusions_leading_to_this_file,
                            test_case_handling_setup,
                            sub_test_suites,
                            test_cases)


class MatchesTestSuite(ValueAssertionBase[structure.TestSuite]):
    def __init__(self,
                 source_file: ValueAssertion[Path],
                 file_inclusions_leading_to_this_file: ValueAssertion[List[Path]],
                 test_case_handling_setup: ValueAssertion[TestCaseHandlingSetup],
                 sub_test_suites: ValueAssertion[Sequence[structure.TestSuite]],
                 test_cases: ValueAssertion[Sequence[TestCaseFileReference]],
                 ):
        self.source_file = source_file
        self.file_inclusions_leading_to_this_file = file_inclusions_leading_to_this_file
        self.test_case_handling_setup = test_case_handling_setup
        self.sub_test_suites = sub_test_suites
        self.test_cases = test_cases

    def _apply(self,
               put: unittest.TestCase,
               value: structure.TestSuite,
               message_builder: MessageBuilder):
        assertion = asrt.and_([
            asrt.sub_component('source_file',
                               structure.TestSuite.source_file.fget,
                               self.source_file),
            asrt.sub_component('file_inclusions_leading_to_this_file',
                               structure.TestSuite.file_inclusions_leading_to_this_file.fget,
                               self.file_inclusions_leading_to_this_file),
            asrt.sub_component('test_case_handling_setup',
                               structure.TestSuite.test_case_handling_setup.fget,
                               self.test_case_handling_setup),
            asrt.sub_component('sub_test_suites',
                               structure.TestSuite.sub_test_suites.fget,
                               self.sub_test_suites),
            asrt.sub_component('test_cases',
                               structure.TestSuite.test_cases.fget,
                               self.test_cases),
        ])
        assertion.apply(put, value, message_builder)
