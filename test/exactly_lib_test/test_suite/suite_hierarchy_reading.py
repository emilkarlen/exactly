import pathlib
import unittest

from exactly_lib.act_phase_setups import command_line
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import test_case_reference_of_source_file
from exactly_lib.test_suite import structure
from exactly_lib.test_suite.instruction_set.parse import SuiteFileReferenceError, SuiteSyntaxError, \
    SuiteDoubleInclusion
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.test_suite.test_resources import check_exception, check_structure
from exactly_lib_test.test_suite.test_resources.check_structure import equals_test_suite
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestInvalidFileSyntax))
    ret_val.addTest(unittest.makeSuite(TestInvalidFileReferences))
    ret_val.addTest(unittest.makeSuite(TestStructure))
    return ret_val


T_C_H_S = TestCaseHandlingSetup(command_line.act_phase_setup(),
                                IDENTITY_PREPROCESSOR)


class MainSuiteWithTwoReferencedCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [
                test_case_reference_of_source_file(root_path / '1.case'),
                test_case_reference_of_source_file(root_path / 'sub' / '2.case')
            ]))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[cases]',
                                                '1.case',
                                                'sub/2.case',
                                                ])),
                            empty_file('1.case'),
                            Dir('sub',
                                [empty_file('2.case')])])


class InvalidCaseContentShouldNotCauseParsingToFail(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [
                test_case_reference_of_source_file(root_path / 'case-with-invalid-content.case'),
            ]))

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

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
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
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                '1.suite',
                                                'sub/2.suite',
                                                ])),
                            empty_file('1.suite'),
                            Dir('sub',
                                [empty_file('2.suite')])])


class MainSuiteWithAbsoluteReferencesToSuitesAndCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
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
                test_case_reference_of_source_file(root_path / '1.case'),
            ],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                str(root_path / '1.suite'),
                                                '[cases]',
                                                str(root_path / '1.case'),
                                                ])),
                            empty_file('1.suite'),
                            empty_file('1.case'),
                            ])


class MainSuiteWithReferencedSuitesAndCasesAndMixedSections(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
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
                test_case_reference_of_source_file(root_path / '1.case'),
                test_case_reference_of_source_file(root_path / 'sub' / '2.case')
            ],
        ))

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
                            empty_file('1.suite'),
                            empty_file('1.case'),
                            Dir('sub',
                                [empty_file('2.suite'),
                                 empty_file('2.case')])])


class ComplexStructure(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return root_path / 'complex.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[structure.TestSuite]:
        return equals_test_suite(structure.TestSuite(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                structure.TestSuite(
                    root_path / 'local.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(root_path / 'from-local-suite.case')]),
                structure.TestSuite(
                    root_path / 'sub' / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [structure.TestSuite(
                        root_path / 'sub' / 'sub-sub.suite',
                        [self.root_suite_based_at(root_path), root_path / 'sub' / 'sub.suite'],
                        T_C_H_S,
                        [],
                        [test_case_reference_of_source_file(root_path / 'sub' / 'sub-sub.case')]
                    )],
                    [test_case_reference_of_source_file(root_path / 'sub' / 'sub.case')]),
            ],
            [test_case_reference_of_source_file(root_path / 'from-main-suite.case')]
        ))

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
                            empty_file('from-main-suite.case'),
                            empty_file('from-local-suite.case'),
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
                                    empty_file('sub.case'),
                                    empty_file('sub-sub.case'),
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
        assert_equals_line_sequence(put,
                                    single_line_sequence(2, 'does-not_exist.case'),
                                    actual.source)


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
        assert_equals_line_sequence(put,
                                    single_line_sequence(1, '[invalid-section]'),
                                    actual.source)


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
        assert_equals_line_sequence(put,
                                    single_line_sequence(2, 'does-not_exist.suite'),
                                    actual.source)


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
        assert_equals_line_sequence(put,
                                    single_line_sequence(2, 'main.suite'),
                                    actual.source)
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
                                    empty_file('in-subdir.suite')
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
        assert_equals_line_sequence(put,
                                    single_line_sequence(3, 'subdir/in-subdir.suite'),
                                    actual.source)
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
