import pathlib
import unittest

from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.test_case.test_case_processing import TestCaseSetup
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.instruction_set.parse import SuiteFileReferenceError, SuiteSyntaxError, \
    SuiteDoubleInclusion
from exactly_lib.util import line_source
from exactly_lib.util.string import lines_content
from exactly_lib_test.section_document.test_resources import assert_equals_line
from exactly_lib_test.test_resources.file_structure import DirContents, File, Dir
from exactly_lib_test.test_suite.test_resources import check_exception, check_structure

T_C_H_S = TestCaseHandlingSetup(single_command_setup.act_phase_setup(),
                                IDENTITY_PREPROCESSOR)


class MainSuiteWithTwoReferencedCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> structure.TestSuite:
        return structure.TestSuite(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [
                TestCaseSetup(root_path / '1.case'),
                TestCaseSetup(root_path / 'sub' / '2.case')
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
            T_C_H_S,
            [],
            [
                TestCaseSetup(root_path / 'case-with-invalid-content.case'),
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
            [],
            T_C_H_S,
            [
                structure.TestSuite(
                    root_path / '1.suite', [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], []),
                structure.TestSuite(
                    root_path / 'sub' / '2.suite', [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], [])
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
            [],
            T_C_H_S,
            [
                structure.TestSuite(root_path / '1.suite',
                                    [self.root_suite_based_at(root_path)],
                                    T_C_H_S,
                                    [], []),
            ],
            [
                TestCaseSetup(root_path / '1.case'),
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
            [],
            T_C_H_S,
            [
                structure.TestSuite(
                    root_path / '1.suite', [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], []),
                structure.TestSuite(
                    root_path / 'sub' / '2.suite', [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], [])
            ],
            [
                TestCaseSetup(root_path / '1.case'),
                TestCaseSetup(root_path / 'sub' / '2.case')
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
            [],
            T_C_H_S,
            [
                structure.TestSuite(
                    root_path / 'local.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [TestCaseSetup(root_path / 'from-local-suite.case')]),
                structure.TestSuite(
                    root_path / 'sub' / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [structure.TestSuite(
                        root_path / 'sub' / 'sub-sub.suite',
                        [self.root_suite_based_at(root_path), root_path / 'sub' / 'sub.suite'],
                        T_C_H_S,
                        [],
                        [TestCaseSetup(root_path / 'sub' / 'sub-sub.case')]
                    )],
                    [TestCaseSetup(root_path / 'sub' / 'sub.case')]),
            ],
            [TestCaseSetup(root_path / 'from-main-suite.case')]
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


class DoubleInclusionOfMainFileFromMainFile(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                'main.suite',
                                                ])),
                            ])

    def expected_exception_class(self):
        return SuiteDoubleInclusion

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteDoubleInclusion)
        put.assertEqual(str(self.root_suite_based_at(root_path)),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line(put,
                           line_source.Line(2, 'main.suite'),
                           actual.line)
        put.assertEqual(self.root_suite_based_at(root_path),
                        actual.included_suite_file,
                        'File that is included twice')
        put.assertEqual(None,
                        actual.first_referenced_from,
                        'File that first included the suite file')


class DoubleInclusionOfSuiteInSubDir(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                'local-1.suite',
                                                'local-2.suite',
                                                ])),
                            File('local-1.suite',
                                 lines_content(['[suites]',
                                                'subdir/in-subdir.suite',
                                                ])),
                            File('local-2.suite',
                                 lines_content(['[suites]',
                                                '',
                                                'subdir/in-subdir.suite',
                                                ])),
                            Dir('subdir',
                                [
                                    File('in-subdir.suite', '')
                                ])
                            ])

    def expected_exception_class(self):
        return SuiteDoubleInclusion

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteDoubleInclusion)
        put.assertEqual(str(root_path / 'local-2.suite'),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line(put,
                           line_source.Line(3, 'subdir/in-subdir.suite'),
                           actual.line)
        put.assertEqual(root_path / 'subdir' / 'in-subdir.suite',
                        actual.included_suite_file,
                        'File that is included twice')
        put.assertEqual(root_path / 'local-1.suite',
                        actual.first_referenced_from,
                        'File that first included the suite file')


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

    def test_double_inclusion_of_main_file_from_main_file(self):
        check_exception.check(DoubleInclusionOfMainFileFromMainFile(), self)

    def test_double_inclusion_of_suite_in_sub_dir(self):
        check_exception.check(DoubleInclusionOfSuiteInSubDir(), self)


class TestInvalidFileSyntax(unittest.TestCase):
    def test_invalid_section(self):
        check_exception.check(SuiteFileSyntaxError(), self)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestInvalidFileSyntax))
    ret_val.addTest(unittest.makeSuite(TestInvalidFileReferences))
    ret_val.addTest(unittest.makeSuite(TestStructure))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
