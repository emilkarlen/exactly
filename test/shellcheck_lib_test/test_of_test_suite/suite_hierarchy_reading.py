import pathlib
import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib.test_suite import structure
from shellcheck_lib.test_suite.parse import SuiteFileReferenceError, SuiteSyntaxError
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
            self.root_suite_based_at(root_path),
            [],
            [
                structure.TestCase(root_path / '1.case'),
                structure.TestCase(root_path / 'sub' / '2.case')
            ])

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[cases]',
                                                '1.case',
                                                'sub/2.case',
                                                ])),
                            File('1.case', ''),
                            Dir('sub',
                                [File('2.case', '')])])


class InvalidCaseContentShouldNotCauseParsingToFail(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [],
            [
                structure.TestCase(root_path / 'case-with-invalid-content.case'),
            ])

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[cases]',
                                                'case-with-invalid-content.case',
                                                ])),
                            File('case-with-invalid-content.case',
                                 'invalid content in test case'),
                            ])


class MainSuiteWithTwoReferencedSuites(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [
                structure.TestSuite(root_path / '1.suite', [], []),
                structure.TestSuite(root_path / 'sub' / '2.suite', [], [])
            ],
            [],
        )

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                '1.suite',
                                                'sub/2.suite',
                                                ])),
                            File('1.suite', ''),
                            Dir('sub',
                                [File('2.suite', '')])])


class MainSuiteWithAbsoluteReferencesToSuitesAndCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [
                structure.TestSuite(root_path / '1.suite', [], []),
            ],
            [
                structure.TestCase(root_path / '1.case'),
            ],
        )

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                str(root_path / '1.suite'),
                                                '[cases]',
                                                str(root_path / '1.case'),
                                                ])),
                            File('1.suite', ''),
                            File('1.case', ''),
                            ])


class MainSuiteWithReferencedSuitesAndCasesAndMixedSections(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [
                structure.TestSuite(root_path / '1.suite', [], []),
                structure.TestSuite(root_path / 'sub' / '2.suite', [], [])
            ],
            [
                structure.TestCase(root_path / '1.case'),
                structure.TestCase(root_path / 'sub' / '2.case')
            ],
        )

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                '1.suite',
                                                '[cases]',
                                                '1.case',
                                                '[suites]',
                                                'sub/2.suite',
                                                '[cases]',
                                                'sub/2.case',
                                                ])),
                            File('1.suite', ''),
                            File('1.case', ''),
                            Dir('sub',
                                [File('2.suite', ''),
                                 File('2.case', '')])])


class ComplexStructure(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'complex.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [
                structure.TestSuite(
                    root_path / 'local.suite',
                    [],
                    [structure.TestCase(root_path / 'from-local-suite.case')]),
                structure.TestSuite(
                    root_path / 'sub' / 'sub.suite',
                    [structure.TestSuite(
                        root_path / 'sub' / 'sub-sub.suite',
                        [],
                        [structure.TestCase(root_path / 'sub' / 'sub-sub.case')]
                    )],
                    [structure.TestCase(root_path / 'sub' / 'sub.case')]),
            ],
            [structure.TestCase(root_path / 'from-main-suite.case')]
        )

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('complex.suite',
                                 lines_content(['[suites]',
                                                'local.suite',
                                                'sub/sub.suite',
                                                '[cases]',
                                                'from-main-suite.case',
                                                ])),
                            File('local.suite',
                                 lines_content(['[cases]',
                                                'from-local-suite.case'])),
                            File('from-main-suite.case', ''),
                            File('from-local-suite.case', ''),
                            Dir('sub',
                                [
                                    File('sub.suite',
                                         lines_content(['[suites]',
                                                        'sub-sub.suite',
                                                        '[cases]',
                                                        'sub.case',
                                                        ])),
                                    File('sub-sub.suite',
                                         lines_content(['[cases]',
                                                        'sub-sub.case',
                                                        ])),
                                    File('sub.case', ''),
                                    File('sub-sub.case', ''),
                                ])
                            ])


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


class SuiteFileSyntaxError(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[invalid-section]',
                                                ])),
                            ])

    def expected_exception_class(self):
        return SuiteSyntaxError

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteSyntaxError)
        put.assertEqual(str(self.root_suite_based_at(root_path)),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line(put,
                           line_source.Line(1, '[invalid-section]'),
                           actual.line)


class ReferencedSuiteFileDoesNotExist(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                'does-not_exist.suite',
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
                           line_source.Line(2, 'does-not_exist.suite'),
                           actual.line)


class TestStructure(unittest.TestCase):
    def test_main_suite_with_two_referenced_cases(self):
        check_structure.check(MainSuiteWithTwoReferencedCases(), self)

    def test_main_suite_with_two_referenced_suites(self):
        check_structure.check(MainSuiteWithTwoReferencedSuites(), self)

    def test_invalid_case_content_should_not_cause_parsing_to_fail(self):
        check_structure.check(InvalidCaseContentShouldNotCauseParsingToFail(), self)

    def test_absolute_references_to_suites_and_cases(self):
        check_structure.check(MainSuiteWithAbsoluteReferencesToSuitesAndCases(), self)

    def test_main_suite_with_referenced_suites_and_cases_and_mixed_sections(self):
        check_structure.check(MainSuiteWithReferencedSuitesAndCasesAndMixedSections(), self)

    def test_complex_structure(self):
        check_structure.check(ComplexStructure(), self)


class TestInvalidFileReferences(unittest.TestCase):
    def test_referenced_case_file_does_not_exist(self):
        check_exception.check(ReferencedCaseFileDoesNotExist(), self)

    def test_referenced_suite_file_does_not_exist(self):
        check_exception.check(ReferencedSuiteFileDoesNotExist(), self)


class TestInvalidFileSyntax(unittest.TestCase):
    def test_invalid_section(self):
        check_exception.check(SuiteFileSyntaxError(), self)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestInvalidFileSyntax))
    ret_val.addTest(unittest.makeSuite(TestInvalidFileReferences))
    ret_val.addTest(unittest.makeSuite(TestStructure))
    return ret_val


if __name__ == '__main__':
    unittest.main()
