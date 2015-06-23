import os
import pathlib
import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib.test_suite import structure

from shellcheck_lib.test_suite.parse import SuiteFileReferenceError
from shellcheck_lib_test.document.test_resources import assert_equals_line
from shellcheck_lib_test.util.file_structure import DirContents, File, Dir
from shellcheck_lib_test.util.with_tmp_file import lines_content
from shellcheck_lib_test.test_of_test_suite.util import check_exception
from shellcheck_lib_test.test_of_test_suite.util import check_structure


class MainSuiteWithTwoReferencedCases(check_structure.Setup):
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


class MainSuiteWithTwoReferencedSuits(check_structure.Setup):
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


class ReferencedCaseFileDoesNotExist(check_exception.Setup):
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


class TestStructure(unittest.TestCase):
    def test_main_suite_with_two_referenced_cases(self):
        check_structure.check(MainSuiteWithTwoReferencedCases(), self)

    def test_main_suite_with_two_referenced_suits(self):
        check_structure.check(MainSuiteWithTwoReferencedSuits(), self)


class TestInvalidFileReferences(unittest.TestCase):
    def test_referenced_case_file_does_not_exist(self):
        check_exception.check(ReferencedCaseFileDoesNotExist(), self)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestStructure))
    ret_val.addTest(unittest.makeSuite(TestInvalidFileReferences))
    return ret_val


if __name__ == '__main__':
    unittest.main()
