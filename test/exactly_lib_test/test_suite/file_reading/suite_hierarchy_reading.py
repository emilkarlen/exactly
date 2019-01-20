import unittest

import pathlib
from pathlib import Path

from exactly_lib.actors import command_line
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import test_case_reference_of_source_file
from exactly_lib.test_suite.file_reading.exception import SuiteFileReferenceError, SuiteSyntaxError, \
    SuiteDoubleInclusion
from exactly_lib.test_suite.structure import TestSuiteHierarchy
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.test_suite.file_reading.test_resources import check_structure, check_exception
from exactly_lib_test.test_suite.file_reading.test_resources.check_structure import equals_test_suite
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidFileSyntax),
        unittest.makeSuite(TestInvalidFileReferences),
        unittest.makeSuite(TestStructure),
    ])


T_C_H_S = TestCaseHandlingSetup(ActPhaseSetup(command_line.actor()),
                                IDENTITY_PREPROCESSOR)


class MainSuiteWithTwoReferencedCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [
                test_case_reference_of_source_file(Path('1.case')),
                test_case_reference_of_source_file(Path('sub') / '2.case')
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
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [
                test_case_reference_of_source_file(Path('case-with-invalid-content.case')),
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
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    Path('1.suite'), [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], []),
                TestSuiteHierarchy(
                    Path('sub') / '2.suite', [self.root_suite_based_at(root_path)],
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
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(root_path / '1.suite',
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
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    Path('1.suite'), [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], []),
                TestSuiteHierarchy(
                    Path('sub') / '2.suite', [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [], [])
            ],
            [
                test_case_reference_of_source_file(Path('1.case')),
                test_case_reference_of_source_file(Path('sub') / '2.case')
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


class MainSuiteWithSuiteInSubDirWithCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    Path('sub-dir') / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(Path('sub-dir') / 'sub.case')],
                ),
            ],
            [],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[suites]',
                                                'sub-dir/sub.suite',
                                                ])),
                            Dir('sub-dir',
                                [File('sub.suite', lines_content([
                                    'sub.case',
                                ])),
                                 empty_file('sub.case')])])


class MainSuiteInSubDirWithCasesAndSuiteInSubDirWithCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        dir_with_sub_suite = Path('main-sub-dir') / 'suite-sub-dir'
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    dir_with_sub_suite / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(dir_with_sub_suite / 'sub.case')],
                ),
            ],
            [test_case_reference_of_source_file(Path('main-sub-dir') / 'main.case')],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            Dir('main-sub-dir', [
                File('main.suite',
                     lines_content([
                         '[cases]',
                         'main.case',
                         '[suites]',
                         'suite-sub-dir/sub.suite',
                     ])),
                empty_file('main.case'),
                Dir('suite-sub-dir',
                    [
                        File('sub.suite', lines_content([
                            'sub.case',
                        ])),
                        empty_file('sub.case')]),
            ])
        ])


class MainSuiteInSubDirWithCasesInSuperDir(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [],
            [test_case_reference_of_source_file(Path('main-sub-dir') / '..' / 'main.case')],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            Dir('main-sub-dir', [
                File('main.suite',
                     lines_content([
                         '[cases]',
                         '../main.case',
                     ])),
            ]),
            empty_file('main.case'),
        ])


class MainSuiteInSubDirWithSuiteWithCasesInSuperDir(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        dir_with_sub_suite = Path('main-sub-dir') / '..'
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    dir_with_sub_suite / 'super.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(dir_with_sub_suite / 'super.case')],
                )
            ],
            [],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            Dir('main-sub-dir', [
                File('main.suite',
                     lines_content([
                         '[suites]',
                         '../super.suite',
                     ])),
            ]),
            File('super.suite', lines_content([
                'super.case',
            ])),
            empty_file('super.case'),
        ])


class MainSuiteInSubDirAndSuiteInSubDirWithCasesReferencedViaWildCards(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        dir_with_sub_suite = Path('main-sub-dir') / 'suite-sub-dir'
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    dir_with_sub_suite / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(dir_with_sub_suite / 'sub.case')],
                ),
            ],
            [],
        ))

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        return DirContents([
            Dir('main-sub-dir', [
                File('main.suite',
                     lines_content([
                         '[suites]',
                         'suite-sub-dir/sub.suite',
                     ])),
                Dir('suite-sub-dir',
                    [
                        File('sub.suite', lines_content([
                            '*.case',
                        ])),
                        empty_file('sub.case')]),
            ])
        ])


class ComplexStructure(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('complex.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> ValueAssertion[TestSuiteHierarchy]:
        return equals_test_suite(TestSuiteHierarchy(
            self.root_suite_based_at(root_path),
            [],
            T_C_H_S,
            [
                TestSuiteHierarchy(
                    Path('local.suite'),
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [],
                    [test_case_reference_of_source_file(Path('from-local-suite.case'))]),
                TestSuiteHierarchy(
                    Path('sub') / 'sub.suite',
                    [self.root_suite_based_at(root_path)],
                    T_C_H_S,
                    [TestSuiteHierarchy(
                        Path('sub') / 'sub-sub.suite',
                        [self.root_suite_based_at(root_path), Path('sub') / 'sub.suite'],
                        T_C_H_S,
                        [],
                        [test_case_reference_of_source_file(Path('sub') / 'sub-sub.case')]
                    )],
                    [test_case_reference_of_source_file(Path('sub') / 'sub.case')]),
            ],
            [test_case_reference_of_source_file(Path('from-main-suite.case'))]
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
        return Path('main.suite')

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
        return Path('main.suite')

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
        return Path('main.suite')

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
        return Path('main.suite')

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
        return Path('main.suite')

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
        put.assertEqual(str(Path('local-2.suite')),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line_sequence(put,
                                    single_line_sequence(3, 'subdir/in-subdir.suite'),
                                    actual.source)
        put.assertEqual(Path('subdir') / 'in-subdir.suite',
                        actual.included_suite_file,
                        'File that is included twice')
        put.assertEqual(Path('local-1.suite'),
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

    def test_main_suite_with_suite_in_sub_dir_with_cases(self):
        check_structure.check(MainSuiteWithSuiteInSubDirWithCases(), self)

    def test_main_suite_in_sub_dir_with_cases_and_suite_in_sub_dir_with_cases(self):
        check_structure.check(MainSuiteInSubDirWithCasesAndSuiteInSubDirWithCases(), self)

    def test_main_suite_with_referenced_suites_and_cases_and_mixed_sections(self):
        check_structure.check(MainSuiteWithReferencedSuitesAndCasesAndMixedSections(), self)

    def test_main_suite_in_sub_dir_with_cases_in_super_dir(self):
        check_structure.check(MainSuiteInSubDirWithCasesInSuperDir(), self)

    def test_main_suite_in_sub_dir_with_suite_with_cases_in_super_dir(self):
        check_structure.check(MainSuiteInSubDirWithSuiteWithCasesInSuperDir(), self)

    def test_complex_structure(self):
        check_structure.check(ComplexStructure(), self)

    def test_main_suite_in_sub_dir_and_suite_in_sub_dir_with_cases_referenced_via_wild_cards(self):
        check_structure.check(MainSuiteInSubDirAndSuiteInSubDirWithCasesReferencedViaWildCards(), self)


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
