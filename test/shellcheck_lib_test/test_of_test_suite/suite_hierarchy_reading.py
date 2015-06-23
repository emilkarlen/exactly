import os
import pathlib
import tempfile
import unittest

from shellcheck_lib.general import line_source

from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.parse import SuiteFileReferenceError
from shellcheck_lib.test_suite.suite_hierarchy_reading import read
from shellcheck_lib_test.document.test_resources import assert_equals_line
from shellcheck_lib_test.util.file_structure import DirContents, File, Dir
from shellcheck_lib_test.util.with_tmp_file import lines_content


class FileStructureAndExpectedException:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self) -> DirContents:
        raise NotImplementedError()

    def expected_exception_class(self):
        raise NotImplementedError()

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        raise NotImplementedError()


class FileStructureAndExpectedHierarchy:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self) -> DirContents:
        raise NotImplementedError()

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        raise NotImplementedError()


class MainSuiteWithTwoReferencedCases(FileStructureAndExpectedHierarchy):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            [],
            [
                structure.TestCase(root_path / '1.case'),
                structure.TestCase(root_path / 'sub' / '2.case')
            ])

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[cases]',
                                                '1.case',
                                                os.path.join('sub', '2.case'),
                                                ])),
                            File('1.case', ''),
                            Dir('sub',
                                [File('2.case', '')])])


class MainSuiteWithTwoReferencedSuits(FileStructureAndExpectedHierarchy):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            [
                structure.TestSuite([], []),
                structure.TestSuite([], [])
            ],
            [],
        )

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suits]',
                                                '1.suite',
                                                os.path.join('sub', '2.suite'),
                                                ])),
                            File('1.suite', ''),
                            Dir('sub',
                                [File('2.suite', '')])])


class ReferencedCaseFileDoesNotExist(FileStructureAndExpectedException):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[cases]',
                                                'does-not_exist.case',
                                                ])),
                            ])

    def expected_exception_class(self):
        return SuiteFileReferenceError

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteFileReferenceError)
        put.assertEqual(str(self.root_suite_based_at(root_path)),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line(put,
                           line_source.Line(2, 'does-not_exist.case'),
                           actual.line)


class TestRead(unittest.TestCase):
    def test_main_suite_with_two_referenced_cases(self):
        check(MainSuiteWithTwoReferencedCases(), self)

    def test_main_suite_with_two_referenced_suits(self):
        check(MainSuiteWithTwoReferencedSuits(), self)


class TestInvalidFileReferences(unittest.TestCase):
    def test_referenced_case_file_does_not_exist(self):
        check_exception(ReferencedCaseFileDoesNotExist(), self)


def check(setup: FileStructureAndExpectedHierarchy,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure_to_read().write_to(tmp_dir_path)
        actual = read(setup.root_suite_based_at(tmp_dir_path))
        expected = setup.expected_structure_based_at(tmp_dir_path)

        StructureEqualityChecker(put).check_suite(expected,
                                                  actual)


def check_exception(setup: FileStructureAndExpectedException,
                    put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as tmp_dir:
        tmp_dir_path = pathlib.Path(tmp_dir)
        setup.file_structure_to_read().write_to(tmp_dir_path)
        with put.assertRaises(Exception) as cm:
            read(setup.root_suite_based_at(tmp_dir_path))
        setup.check_exception(tmp_dir_path, cm.exception, put)


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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRead))
    ret_val.addTest(unittest.makeSuite(TestInvalidFileReferences))
    return ret_val


if __name__ == '__main__':
    unittest.main()
