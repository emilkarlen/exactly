import pathlib
import tempfile
import unittest

from shellcheck_lib.test_suite import structure

from shellcheck_lib.test_suite.suite_hierarchy_reading import read
from shellcheck_lib_test.util.file_structure import DirContents


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self) -> DirContents:
        raise NotImplementedError()

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        raise NotImplementedError()


def check(setup: Setup,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure_to_read().write_to(tmp_dir_path)
        actual = read(setup.root_suite_based_at(tmp_dir_path))
        expected = setup.expected_structure_based_at(tmp_dir_path)

        StructureEqualityChecker(put).check_suite(expected,
                                                  actual)


class StructureEqualityChecker:
    def __init__(self,
                 put: unittest.TestCase):
        self.put = put

    def check_suite(self,
                    expected: structure.TestSuite,
                    actual: structure.TestSuite):
        self.put.assertEqual(len(expected.sub_test_suites),
                             len(actual.sub_test_suites),
                             'Number of sub suites')

        self.put.assertEqual(len(expected.test_cases),
                             len(actual.test_cases),
                             'Number of cases in the suite')

        for expected_case, actual_case in zip(expected.test_cases, actual.test_cases):
            self.check_case(expected_case, actual_case)

        for expected_suite, actual_suite in zip(expected.sub_test_suites, actual.sub_test_suites):
            self.check_suite(expected_suite, actual_suite)

    def check_case(self,
                   expected: structure.TestCase,
                   actual: structure.TestCase):
        self.put.assertEqual(expected.file_path,
                             actual.file_path,
                             'File path of test case')
