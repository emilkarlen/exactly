import pathlib
import unittest
from pathlib import Path

from exactly_lib.definitions.entity.directives import INCLUDING_DIRECTIVE_INFO
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import test_case_reference_of_source_file
from exactly_lib.section_document import exceptions as sec_doc_exceptions
from exactly_lib.section_document.source_location import SourceLocationPath, SourceLocation
from exactly_lib.test_suite.file_reading.exception import SuiteFileReferenceError, SuiteParseError, \
    SuiteDoubleInclusion
from exactly_lib.test_suite.structure import TestSuiteHierarchy
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.processing.test_resources.act_phase import command_line_actor_setup
from exactly_lib_test.section_document.test_resources.source_location_assertions import equals_source_location_path
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.test_suite.file_reading.test_resources import check_structure, check_exception
from exactly_lib_test.test_suite.file_reading.test_resources.check_structure import equals_test_suite
from exactly_lib_test.test_suite.file_reading.test_resources.exception_assertions import matches_suite_parse_error
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence, \
    equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidFileSyntax),
        unittest.makeSuite(TestInvalidCaseOrSuiteFileReferences),
        unittest.makeSuite(TestStructure),
        unittest.makeSuite(TestInvalidInclusionDirectiveFileReferences),
    ])


T_C_H_S = TestCaseHandlingSetup(command_line_actor_setup(),
                                IDENTITY_PREPROCESSOR)


class MainSuiteWithTwoReferencedCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.CASES.syntax,
                                                '1.case',
                                                'sub/2.case',
                                                ])),
                            File.empty('1.case'),
                            Dir('sub',
                                [File.empty('2.case')])])


class InvalidCaseContentShouldNotCauseParsingToFail(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.CASES.syntax,
                                                'case-with-invalid-content.case',
                                                ])),
                            File('case-with-invalid-content.case',
                                 'invalid content in test case'),
                            ])


class MainSuiteWithTwoReferencedSuites(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.SUITES.syntax,
                                                '1.suite',
                                                'sub/2.suite',
                                                ])),
                            File.empty('1.suite'),
                            Dir('sub',
                                [File.empty('2.suite')])])


class MainSuiteWithAbsoluteReferencesToSuitesAndCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.SUITES.syntax,
                                                str(root_path / '1.suite'),
                                                section_names.CASES.syntax,
                                                str(root_path / '1.case'),
                                                ])),
                            File.empty('1.suite'),
                            File.empty('1.case'),
                            ])


class MainSuiteWithReferencedSuitesAndCasesAndMixedSections(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.SUITES.syntax,
                                                '1.suite',
                                                section_names.CASES.syntax,
                                                '1.case',
                                                section_names.SUITES.syntax,
                                                'sub/2.suite',
                                                section_names.CASES.syntax,
                                                'sub/2.case',
                                                ])),
                            File.empty('1.suite'),
                            File.empty('1.case'),
                            Dir('sub',
                                [File.empty('2.suite'),
                                 File.empty('2.case')])])


class MainSuiteWithSuiteInSubDirWithCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.SUITES.syntax,
                                                'sub-dir/sub.suite',
                                                ])),
                            Dir('sub-dir',
                                [File('sub.suite', lines_content([
                                    'sub.case',
                                ])),
                                 File.empty('sub.case')])])


class MainSuiteInSubDirWithCasesAndSuiteInSubDirWithCases(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                         section_names.CASES.syntax,
                         'main.case',
                         section_names.SUITES.syntax,
                         'suite-sub-dir/sub.suite',
                     ])),
                File.empty('main.case'),
                Dir('suite-sub-dir',
                    [
                        File('sub.suite', lines_content([
                            'sub.case',
                        ])),
                        File.empty('sub.case')]),
            ])
        ])


class MainSuiteInSubDirWithCasesInSuperDir(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                         section_names.CASES.syntax,
                         '../main.case',
                     ])),
            ]),
            File.empty('main.case'),
        ])


class MainSuiteInSubDirWithSuiteWithCasesInSuperDir(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                         section_names.SUITES.syntax,
                         '../super.suite',
                     ])),
            ]),
            File('super.suite', lines_content([
                'super.case',
            ])),
            File.empty('super.case'),
        ])


class MainSuiteInSubDirAndSuiteInSubDirWithCasesReferencedViaWildCards(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main-sub-dir') / 'main.suite'

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                         section_names.SUITES.syntax,
                         'suite-sub-dir/sub.suite',
                     ])),
                Dir('suite-sub-dir',
                    [
                        File('sub.suite', lines_content([
                            '*.case',
                        ])),
                        File.empty('sub.case')]),
            ])
        ])


class ComplexStructure(check_structure.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('complex.suite')

    def expected_structure_based_at(self, root_path: pathlib.Path) -> Assertion[TestSuiteHierarchy]:
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
                                 lines_content([section_names.SUITES.syntax,
                                                'local.suite',
                                                'sub/sub.suite',
                                                section_names.CASES.syntax,
                                                'from-main-suite.case',
                                                ])),
                            File('local.suite',
                                 lines_content([section_names.CASES.syntax,
                                                'from-local-suite.case'])),
                            File.empty('from-main-suite.case'),
                            File.empty('from-local-suite.case'),
                            Dir('sub',
                                [
                                    File('sub.suite',
                                         lines_content([section_names.SUITES.syntax,
                                                        'sub-sub.suite',
                                                        section_names.CASES.syntax,
                                                        'sub.case',
                                                        ])),
                                    File('sub-sub.suite',
                                         lines_content([section_names.CASES.syntax,
                                                        'sub-sub.case',
                                                        ])),
                                    File.empty('sub.case'),
                                    File.empty('sub-sub.case'),
                                ])
                            ])


class ReferencedCaseFileDoesNotExist(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content([section_names.CASES.syntax,
                                                'does-not_exist.case',
                                                ])),
                            ])

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


class ReferencedInclusionDirectiveFileDoesNotExist(check_exception.Setup):
    file_inclusion_line = ' '.join([INCLUDING_DIRECTIVE_INFO.singular_name,
                                    'does-not-exist.txt'])
    root_suite_file = Path('main.suite')

    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return self.root_suite_file

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File(self.root_suite_file.name,
                                 lines_content([phase_names.SETUP.syntax,
                                                self.file_inclusion_line,
                                                ])),
                            ])

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteParseError)

        expected_source = single_line_sequence(2, self.file_inclusion_line)

        expectation = matches_suite_parse_error(
            suite_file=asrt.equals(self.root_suite_based_at(root_path)),
            maybe_section_name=asrt.equals(phase_names.SETUP.plain),
            source=equals_line_sequence(expected_source),
            source_location=equals_source_location_path(
                SourceLocationPath(
                    SourceLocation(
                        expected_source,
                        self.root_suite_file,
                    ),
                    []
                )
            ),
            document_parser_exception=asrt.is_instance(sec_doc_exceptions.FileAccessError),
        )

        expectation.apply(put, actual)


class ReferencedInclusionDirectiveFileInIncludedFileDoesNotExist(check_exception.Setup):
    file_1_invalid_inclusion_line = ' '.join([INCLUDING_DIRECTIVE_INFO.singular_name,
                                              'does-not-exist.txt'])

    file_1 = File('1.xly',
                  lines_content([file_1_invalid_inclusion_line]))

    root_suite_inclusion_line = ' '.join([INCLUDING_DIRECTIVE_INFO.singular_name,
                                          file_1.name])
    inclusion_line_in_file_1 = single_line_sequence(1, file_1_invalid_inclusion_line)

    root_suite_file = File('0.suite',
                           lines_content([phase_names.CLEANUP.syntax,
                                          root_suite_inclusion_line,
                                          ]))
    inclusion_line_in_root_file = single_line_sequence(2, root_suite_inclusion_line)

    expected_source_location_path = SourceLocationPath(
        SourceLocation(
            inclusion_line_in_file_1,
            file_1.name_as_path,
        ),
        [
            SourceLocation(
                inclusion_line_in_root_file,
                root_suite_file.name_as_path,
            )
        ]
    )

    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return self.root_suite_file.name_as_path

    def file_structure_to_read(self) -> DirContents:
        return DirContents([self.root_suite_file,
                            self.file_1
                            ])

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteParseError)

        expectation = matches_suite_parse_error(
            suite_file=asrt.equals(self.root_suite_based_at(root_path)),
            maybe_section_name=asrt.equals(phase_names.CLEANUP.plain),
            source=equals_line_sequence(self.inclusion_line_in_file_1),
            source_location=equals_source_location_path(self.expected_source_location_path),
            document_parser_exception=asrt.is_instance(sec_doc_exceptions.FileAccessError),
        )

        expectation.apply(put, actual)


class SuiteFileSyntaxError(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['[invalid-section]',
                                                ])),
                            ])

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteParseError)

        expected_source = single_line_sequence(1, '[invalid-section]')

        expectation = matches_suite_parse_error(
            suite_file=asrt.equals(self.root_suite_based_at(root_path)),
            maybe_section_name=asrt.is_none,
            source=equals_line_sequence(expected_source),
            source_location=equals_source_location_path(
                SourceLocationPath(
                    SourceLocation(
                        expected_source,
                        Path('main.suite'),
                    ),
                    []
                )
            ),
            document_parser_exception=asrt.is_instance(sec_doc_exceptions.FileSourceError),
        )

        expectation.apply(put, actual)


class SuiteFileSyntaxErrorOfMissingClosingQuotation(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content(['"starting but no closing double quote',
                                                ])),
                            ])

    def check_exception(self,
                        root_path: pathlib.Path,
                        actual: Exception,
                        put: unittest.TestCase):
        put.assertIsInstance(actual, SuiteParseError)
        put.assertEqual(str(self.root_suite_based_at(root_path)),
                        str(actual.suite_file),
                        'Source file that contains the error')
        assert_equals_line_sequence(put,
                                    single_line_sequence(1, '"starting but no closing double quote'),
                                    actual.source)


class ReferencedSuiteFileDoesNotExist(check_exception.Setup):
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        return Path('main.suite')

    def file_structure_to_read(self) -> DirContents:
        return DirContents([File('main.suite',
                                 lines_content([section_names.SUITES.syntax,
                                                'does-not_exist.suite',
                                                ])),
                            ])

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
                                 lines_content([section_names.SUITES.syntax,
                                                'main.suite',
                                                ])),
                            ])

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
                                 lines_content([section_names.SUITES.syntax,
                                                'local-1.suite',
                                                'local-2.suite',
                                                ])),
                            File('local-1.suite',
                                 lines_content([section_names.SUITES.syntax,
                                                'subdir/in-subdir.suite',
                                                ])),
                            File('local-2.suite',
                                 lines_content([section_names.SUITES.syntax,
                                                '',
                                                'subdir/in-subdir.suite',
                                                ])),
                            Dir('subdir',
                                [
                                    File.empty('in-subdir.suite')
                                ])
                            ])

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


class TestInvalidCaseOrSuiteFileReferences(unittest.TestCase):
    def test_referenced_case_file_does_not_exist(self):
        check_exception.check(ReferencedCaseFileDoesNotExist(), self)

    def test_referenced_suite_file_does_not_exist(self):
        check_exception.check(ReferencedSuiteFileDoesNotExist(), self)

    def test_double_inclusion_of_main_file_from_main_file(self):
        check_exception.check(DoubleInclusionOfMainFileFromMainFile(), self)

    def test_double_inclusion_of_suite_in_sub_dir(self):
        check_exception.check(DoubleInclusionOfSuiteInSubDir(), self)


class TestInvalidInclusionDirectiveFileReferences(unittest.TestCase):
    def test_referenced_file_does_not_exist__direct(self):
        check_exception.check(ReferencedInclusionDirectiveFileDoesNotExist(), self)

    def test_referenced_file_does_not_exist__indirect(self):
        check_exception.check(ReferencedInclusionDirectiveFileInIncludedFileDoesNotExist(), self)


class TestInvalidFileSyntax(unittest.TestCase):
    def test_invalid_section(self):
        check_exception.check(SuiteFileSyntaxError(), self)

    def test_invalid_path_syntax(self):
        check_exception.check(SuiteFileSyntaxErrorOfMissingClosingQuotation(), self)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
