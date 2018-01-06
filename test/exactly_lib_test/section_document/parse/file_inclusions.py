import unittest
from pathlib import Path, PosixPath, PurePosixPath
from typing import List, Dict, Sequence

from exactly_lib.section_document.document_parser import SectionConfiguration, SectionsConfiguration
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.line_source import SourceLocation, single_line_sequence
from exactly_lib_test.section_document.parse.test_resources.arrangement_and_expectation import Expectation, check, \
    std_conf_arrangement, check_and_expect_exception, \
    Arrangement
from exactly_lib_test.section_document.parse.test_resources.element_parser import SECTION_1_NAME, SECTION_2_NAME, \
    NO_FILE_INCLUSIONS, inclusion_of_file, inclusion_of_list_of_files, ok_instruction, syntax_error_instruction, \
    ARBITRARY_OK_INSTRUCTION_SOURCE_LINE, SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions
from exactly_lib_test.section_document.parse.test_resources.exception_assertions import is_file_source_error, \
    matches_file_source_error, is_file_access_error, matches_file_access_error
from exactly_lib_test.section_document.test_resources.document_assertions import matches_document
from exactly_lib_test.section_document.test_resources.section_contents_elements import \
    equals_instruction_without_description
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, sym_link, file_with_lines, \
    empty_dir_contents, add_dir_contents, Dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileAccessErrorShouldBeRaisedWhenFileIsInvalid),
        unittest.makeSuite(TestInclusionDirectiveIsNotAllowedOutsideOfSection),
        unittest.makeSuite(TestSectionSwitching),
        unittest.makeSuite(TestCombinationOfDocuments),
        unittest.makeSuite(TestMultipleInclusionsOfSameFile),
        unittest.makeSuite(TestInclusionFromInclusion),
    ])


class TestFileAccessErrorShouldBeRaisedWhenFileIsInvalid(unittest.TestCase):
    def _check(self,
               root_source_file_path: Path,
               name_of_invalid_file: str,
               expected_exception: asrt.ValueAssertion[FileAccessError],
               additional_dir_contents: DirContents = empty_dir_contents()):
        # ARRANGE #
        cases = [
            NameAndValue('source file does not exist',
                         DirContents([])
                         ),
            NameAndValue('source file is a directory',
                         DirContents([empty_dir(name_of_invalid_file)])
                         ),
            NameAndValue('symlink to non-existing file',
                         DirContents([sym_link(name_of_invalid_file, 'non-existing-file')])
                         ),
        ]
        for nav in cases:
            dir_contents = add_dir_contents([nav.value, additional_dir_contents])
            with self.subTest(nav.name):
                check_and_expect_exception(
                    self,
                    arrangement=std_conf_arrangement(dir_contents,
                                                     root_source_file_path),
                    expected_exception=is_file_access_error(expected_exception)
                )

    def test_invalid_root_source_file(self):
        # ARRANGE #
        file_name = 'source-file-name'
        root_file_path = Path(file_name)
        self._check(root_file_path,
                    name_of_invalid_file=file_name,
                    expected_exception=matches_file_access_error(root_file_path,
                                                                 []))

    def test_invalid_included_file(self):
        # ARRANGE #
        included_file_name = 'included-file.src'
        root_file = file_with_lines('root-file.src',
                                    [
                                        section_header(SECTION_1_NAME),
                                        inclusion_of_file(included_file_name),
                                    ])
        root_file_path = Path(root_file.file_name)
        self._check(root_file_path,
                    name_of_invalid_file=included_file_name,
                    additional_dir_contents=DirContents([root_file]),
                    expected_exception=matches_file_access_error(
                        Path(included_file_name),
                        [
                            SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                           root_file_path)
                        ]))

    def test_invalid_sub_dir_of_included_file(self):
        # ARRANGE #
        included_file_name_path = PosixPath('non-existing-dir') / 'included-file.src'
        included_file_name = str(included_file_name_path)
        root_file = file_with_lines('root-file.src',
                                    [
                                        section_header(SECTION_1_NAME),
                                        inclusion_of_file(included_file_name),
                                    ])
        root_file_path = Path(root_file.file_name)
        dir_contents = DirContents([root_file])
        expected_exception = matches_file_access_error(
            included_file_name_path,
            [
                SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                               root_file_path)
            ])
        # ACT & ASSERT #
        check_and_expect_exception(
            self,
            arrangement=std_conf_arrangement(dir_contents,
                                             root_file_path),
            expected_exception=is_file_access_error(expected_exception)
        )


class TestInclusionDirectiveIsNotAllowedOutsideOfSection(unittest.TestCase):
    def test_inclusion_directive_SHOULD_not_be_allowed_before_section_declaration_when_there_is_no_default_section(
            self):
        # ARRANGE #
        included_file_lines = [
            section_header(SECTION_1_NAME),
            ARBITRARY_OK_INSTRUCTION_SOURCE_LINE,
        ]
        included_file = file_with_lines('included.src', included_file_lines)

        root_file_lines = [
            inclusion_of_file(included_file.name),
        ]
        root_file = file_with_lines('root.src', root_file_lines)
        root_file_path = Path(root_file.file_name)

        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  DirContents([root_file, included_file]),
                                  root_file_path)
        expected_exception = is_file_source_error(
            matches_file_source_error(
                maybe_section_name=asrt.is_none,
                location_path=[
                    SourceLocation(single_line_sequence(1, inclusion_of_file(included_file.name)),
                                   root_file_path)
                ]))
        # ACT & ASSERT #
        check_and_expect_exception(self, arrangement,
                                   expected_exception)


class SingleFileInclusionCheckSetup:
    def __init__(self,
                 sections_conf: SectionsConfiguration,
                 root_file_lines: List[str],
                 included_file_lines: List[str],
                 expected_doc: Dict[str, Sequence[asrt.ValueAssertion[SectionContentElement]]]
                 ):
        self.sections_conf = sections_conf
        self.root_file_lines = root_file_lines
        self.included_file_lines = included_file_lines
        self.expected_doc = expected_doc


class TestSectionSwitching(unittest.TestCase):
    def test_current_section_of_including_file_SHOULD_become_default_section_of_included_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_name = 'included.src'
        included_file_path = Path(included_file_name)

        instruction_1_in_included_file = ok_instruction('instruction 1 in included file')

        cases = [
            NameAndValue(
                'WHEN including from default section THEN that section SHOULD be default also in included file',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITH_SECTION_1_AS_DEFAULT,
                    root_file_lines=[
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(1, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ])
                        ]
                    }
                )),
            NameAndValue(
                'WHEN including from non-default section THEN that section SHOULD be default in included file',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_2_NAME),
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_2_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_2_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ])
                        ]
                    }
                )),
        ]
        for nav in cases:
            setup = nav.value
            assert isinstance(setup, SingleFileInclusionCheckSetup)
            with self.subTest(nav.name):
                # ACT & ASSERT #
                check_single_file_inclusions(self, setup, root_file_name, included_file_name)

    def test_current_section_of_including_file_SHOULD_not_depend_on_section_switching_in_included_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_name = 'included.src'
        included_file_path = Path(included_file_name)

        instruction_1_in_included_file = ok_instruction('instruction 1 in included file')
        instruction_1_in_root_file = ok_instruction('instruction 1 in root file')

        setup = SingleFileInclusionCheckSetup(
            sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
            root_file_lines=[
                section_header(SECTION_1_NAME),
                inclusion_of_file(included_file_name),
                instruction_1_in_root_file,
            ],
            included_file_lines=[
                section_header(SECTION_2_NAME),
                instruction_1_in_included_file,
            ],
            expected_doc={
                SECTION_1_NAME: [
                    equals_instruction_without_description(
                        3,
                        instruction_1_in_root_file,
                        SECTION_1_NAME,
                        root_file_path,
                        NO_FILE_INCLUSIONS)
                ],
                SECTION_2_NAME: [
                    equals_instruction_without_description(
                        2,
                        instruction_1_in_included_file,
                        SECTION_2_NAME,
                        included_file_path,
                        [
                            SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                           root_file_path)
                        ])
                ],
            }
        )
        # ACT & ASSERT #
        check_single_file_inclusions(self, setup, root_file_name, included_file_name)


class TestCombinationOfDocuments(unittest.TestCase):
    def test_combination_of_instruction_from_root_and_single_included_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_name = 'included.src'
        included_file_path = Path(included_file_name)

        instruction_1_in_included_file = ok_instruction('instruction 1 in included file')
        instruction_1_in_root_file = ok_instruction('instruction 1 in root file')
        instruction_2_in_root_file = ok_instruction('instruction 2 in root file')

        cases = [
            NameAndValue(
                '0 instr in root, 1 instr in included',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ])
                        ]
                    }
                )),
            NameAndValue(
                '1 instr in root, 0 instr in included',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        instruction_1_in_root_file,
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                2,
                                instruction_1_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS)
                        ]
                    }
                )),
            NameAndValue(
                '1 instr in root, 1 instr in included (after root) /same section',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        instruction_1_in_root_file,
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                2,
                                instruction_1_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS),
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(3, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ]
                    }
                )),
            NameAndValue(
                '1 instr in root, 1 instr in included (before root) /same section',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        inclusion_of_file(included_file_name),
                        instruction_1_in_root_file,
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                            equals_instruction_without_description(
                                3,
                                instruction_1_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS),
                        ]
                    }
                )),
            NameAndValue(
                '1 instr in root + 1 instr in included + 1 instr in root  /same section',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        instruction_1_in_root_file,
                        inclusion_of_file(included_file_name),
                        instruction_2_in_root_file,
                    ],
                    included_file_lines=[
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                2,
                                instruction_1_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS),
                            equals_instruction_without_description(
                                1,
                                instruction_1_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(3, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                            equals_instruction_without_description(
                                4,
                                instruction_2_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS),
                        ]
                    }
                )),
            NameAndValue(
                '1 instr in root, 1 instr in included (after root) /different sections',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        instruction_1_in_root_file,
                        inclusion_of_file(included_file_name)
                    ],
                    included_file_lines=[
                        section_header(SECTION_2_NAME),
                        instruction_1_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                2,
                                instruction_1_in_root_file,
                                SECTION_1_NAME,
                                root_file_path,
                                NO_FILE_INCLUSIONS),
                        ],
                        SECTION_2_NAME: [
                            equals_instruction_without_description(
                                2,
                                instruction_1_in_included_file,
                                SECTION_2_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(3, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ]
                    }
                )),
        ]
        for nav in cases:
            setup = nav.value
            assert isinstance(setup, SingleFileInclusionCheckSetup)
            with self.subTest(nav.name):
                # ACT & ASSERT #
                check_single_file_inclusions(self, setup, root_file_name, included_file_name)

    def test_inclusion_of_multiple_files_in_same_directive(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_1_name = 'included-1.src'
        included_file_2_name = 'included-2.src'

        instruction_in_included_file_1 = ok_instruction('instruction in included file 1')
        instruction_in_included_file_2 = ok_instruction('instruction in included file 2')
        instruction_1_in_root_file = ok_instruction('instruction 1 in root file')
        instruction_2_in_root_file = ok_instruction('instruction 1 in root file')

        inclusion_directive_of_file_1_and_2 = inclusion_of_list_of_files([included_file_1_name,
                                                                          included_file_2_name])

        root_file_lines = [
            section_header(SECTION_1_NAME),
            instruction_1_in_root_file,
            inclusion_directive_of_file_1_and_2,
            instruction_2_in_root_file,
        ]

        included_file_1_lines = [
            instruction_in_included_file_1,
        ]

        included_file_2_lines = [
            instruction_in_included_file_2,
        ]

        file_inclusion_chain_of_included_files = [
            SourceLocation(single_line_sequence(3, inclusion_directive_of_file_1_and_2),
                           root_file_path)
        ]

        expected_doc = {
            SECTION_1_NAME: [
                equals_instruction_without_description(
                    2,
                    instruction_1_in_root_file,
                    SECTION_1_NAME,
                    root_file_path,
                    NO_FILE_INCLUSIONS
                ),
                equals_instruction_without_description(
                    1,
                    instruction_in_included_file_1,
                    SECTION_1_NAME,
                    Path(included_file_1_name),
                    file_inclusion_chain_of_included_files),
                equals_instruction_without_description(
                    1,
                    instruction_in_included_file_2,
                    SECTION_1_NAME,
                    Path(included_file_2_name),
                    file_inclusion_chain_of_included_files),
                equals_instruction_without_description(
                    4,
                    instruction_2_in_root_file,
                    SECTION_1_NAME,
                    root_file_path,
                    NO_FILE_INCLUSIONS
                ),
            ],
        }

        root_file = file_with_lines(root_file_name, root_file_lines)
        included_file_1 = file_with_lines(included_file_1_name, included_file_1_lines)
        included_file_2 = file_with_lines(included_file_2_name, included_file_2_lines)
        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  DirContents([root_file,
                                               included_file_1,
                                               included_file_2]),
                                  root_file_path)
        expectation = Expectation(matches_document(expected_doc))
        # ACT & ASSERT #
        check(self, arrangement, expectation)

    def test_inclusion_of_empty_list_of_files(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        instruction_1_in_root_file = ok_instruction('instruction 1 in root file')
        instruction_2_in_root_file = ok_instruction('instruction 1 in root file')

        inclusion_directive_of_file_1_and_2 = inclusion_of_list_of_files([])

        root_file_lines = [
            section_header(SECTION_1_NAME),
            instruction_1_in_root_file,
            inclusion_directive_of_file_1_and_2,
            instruction_2_in_root_file,
        ]

        expected_doc = {
            SECTION_1_NAME: [
                equals_instruction_without_description(
                    2,
                    instruction_1_in_root_file,
                    SECTION_1_NAME,
                    root_file_path,
                    NO_FILE_INCLUSIONS
                ),
                equals_instruction_without_description(
                    4,
                    instruction_2_in_root_file,
                    SECTION_1_NAME,
                    root_file_path,
                    NO_FILE_INCLUSIONS
                ),
            ],
        }

        root_file = file_with_lines(root_file_name, root_file_lines)
        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  DirContents([root_file]),
                                  root_file_path)
        expectation = Expectation(matches_document(expected_doc))
        # ACT & ASSERT #
        check(self, arrangement, expectation)


class TestMultipleInclusionsOfSameFile(unittest.TestCase):
    def test_multiple_inclusions_of_same_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_name = 'included.src'
        included_file_path = Path(included_file_name)

        instruction_in_included_file = ok_instruction('instruction in included file')

        cases = [
            NameAndValue(
                'inclusions in same section',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        inclusion_of_file(included_file_name),
                        inclusion_of_file(included_file_name),
                    ],
                    included_file_lines=[
                        instruction_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(3, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ]
                    }
                )),
            NameAndValue(
                'inclusions via same directive',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        inclusion_of_list_of_files([included_file_name, included_file_name]),
                    ],
                    included_file_lines=[
                        instruction_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(
                                        single_line_sequence(2, inclusion_of_list_of_files([included_file_name,
                                                                                            included_file_name])),
                                        root_file_path)
                                ]),
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(
                                        single_line_sequence(2, inclusion_of_list_of_files([included_file_name,
                                                                                            included_file_name])),
                                        root_file_path)
                                ]),
                        ]
                    }
                )),
            NameAndValue(
                'inclusions in different sections',
                SingleFileInclusionCheckSetup(
                    sections_conf=SECTION_1_AND_2_WITHOUT_DEFAULT,
                    root_file_lines=[
                        section_header(SECTION_1_NAME),
                        inclusion_of_file(included_file_name),
                        section_header(SECTION_2_NAME),
                        inclusion_of_file(included_file_name),
                    ],
                    included_file_lines=[
                        instruction_in_included_file,
                    ],
                    expected_doc={
                        SECTION_1_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ],
                        SECTION_2_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_2_NAME,
                                included_file_path,
                                [
                                    SourceLocation(single_line_sequence(4, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ]
                    }
                )),
        ]
        for nav in cases:
            setup = nav.value
            assert isinstance(setup, SingleFileInclusionCheckSetup)
            with self.subTest(nav.name):
                # ACT & ASSERT #
                check_single_file_inclusions(self, setup, root_file_name, included_file_name)


class SetupWithDoubleInclusionAndIncludedFilesInSubDir:
    def __init__(self, source_line_in_included_file_2_or_none_if_file_should_not_exist: str = None):
        self.sub_dir_of_included_files = 'sub-dir'

        self.instruction_in_root_file = ok_instruction('instruction 1 in root file')

        self.instruction_in_included_file_1 = ok_instruction('instruction 1 in included file 1')
        self.source_line_in_included_file_2 = source_line_in_included_file_2_or_none_if_file_should_not_exist

        self.included_file_2 = file_with_lines('included-file-2.src', [
            (
                self.source_line_in_included_file_2
                if source_line_in_included_file_2_or_none_if_file_should_not_exist is not None
                else ''
            ),
        ])

        self.included_file_1 = file_with_lines('included-file-1.src', [
            inclusion_of_file(self.included_file_2.name),
            self.instruction_in_included_file_1,
        ])

        self.inclusion_of_file_1_from_root_file = inclusion_of_file(
            PurePosixPath(self.sub_dir_of_included_files) / self.included_file_1.name)

        self.root_file = file_with_lines('root.src', [
            section_header(SECTION_1_NAME),
            self.inclusion_of_file_1_from_root_file,
            self.instruction_in_root_file,
        ])
        self.root_file_path = Path(self.root_file.name)

    @property
    def dir_contents(self) -> DirContents:
        files_in_sub_dir = [self.included_file_1]
        if self.source_line_in_included_file_2 is not None:
            files_in_sub_dir.append(self.included_file_2)

        return DirContents([
            self.root_file,
            Dir(self.sub_dir_of_included_files, files_in_sub_dir),
        ])

    @property
    def source_location_of_inclusion_of_file_1_from_root_file(self) -> SourceLocation:
        return SourceLocation(single_line_sequence(2, self.inclusion_of_file_1_from_root_file),
                              self.root_file_path)

    @property
    def source_location_of_inclusion_of_file_2_from_included_file_1(self) -> SourceLocation:
        return SourceLocation(single_line_sequence(1, inclusion_of_file(self.included_file_2.name)),
                              Path(self.sub_dir_of_included_files) / self.included_file_1.name)


class TestInclusionFromInclusion(unittest.TestCase):
    def test_instruction_source_locations(self):
        # ARRANGE #
        setup = SetupWithDoubleInclusionAndIncludedFilesInSubDir(
            source_line_in_included_file_2_or_none_if_file_should_not_exist=ok_instruction(
                'instruction in included file 2'))

        expected_doc = {
            SECTION_1_NAME: [
                equals_instruction_without_description(
                    1,
                    setup.source_line_in_included_file_2,
                    SECTION_1_NAME,
                    Path(setup.included_file_2.name),
                    [
                        setup.source_location_of_inclusion_of_file_1_from_root_file,
                        setup.source_location_of_inclusion_of_file_2_from_included_file_1,
                    ]
                ),
                equals_instruction_without_description(
                    2,
                    setup.instruction_in_included_file_1,
                    SECTION_1_NAME,
                    Path(setup.sub_dir_of_included_files) / setup.included_file_1.name,
                    [
                        setup.source_location_of_inclusion_of_file_1_from_root_file,
                    ]
                ),
                equals_instruction_without_description(
                    3,
                    setup.instruction_in_root_file,
                    SECTION_1_NAME,
                    setup.root_file_path,
                    NO_FILE_INCLUSIONS,
                ),
            ],
        }

        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  setup.dir_contents,
                                  setup.root_file_path,
                                  )
        expectation = Expectation(matches_document(expected_doc))
        # ACT & ASSERT #
        check(self, arrangement, expectation)

    def test_source_locations_of_file_access_error(self):
        # ARRANGE #
        setup = SetupWithDoubleInclusionAndIncludedFilesInSubDir(
            source_line_in_included_file_2_or_none_if_file_should_not_exist=None
        )

        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  setup.dir_contents,
                                  setup.root_file_path,
                                  )
        expected_file_access_error = matches_file_access_error(
            Path(setup.included_file_2.name),
            [
                setup.source_location_of_inclusion_of_file_1_from_root_file,
                setup.source_location_of_inclusion_of_file_2_from_included_file_1,
            ]
        )
        # ACT & ASSERT #
        check_and_expect_exception(self, arrangement,
                                   is_file_access_error(expected_file_access_error))

    def test_source_locations_of_file_source_error(self):
        # ARRANGE #
        error_message = 'the error message'
        setup = SetupWithDoubleInclusionAndIncludedFilesInSubDir(
            source_line_in_included_file_2_or_none_if_file_should_not_exist=syntax_error_instruction(error_message)
        )

        arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                  setup.dir_contents,
                                  setup.root_file_path,
                                  )
        expected_file_source_error = matches_file_source_error(
            asrt.equals(SECTION_1_NAME),
            [
                setup.source_location_of_inclusion_of_file_1_from_root_file,
                setup.source_location_of_inclusion_of_file_2_from_included_file_1,
                SourceLocation(single_line_sequence(1,
                                                    syntax_error_instruction(error_message)),
                               Path(setup.included_file_2.name)),

            ]
        )
        # ACT & ASSERT #
        check_and_expect_exception(self, arrangement,
                                   is_file_source_error(expected_file_source_error))


def check_single_file_inclusions(put: unittest.TestCase,
                                 setup: SingleFileInclusionCheckSetup,
                                 root_file_name: str,
                                 included_file_name: str,
                                 ):
    root_file = file_with_lines(root_file_name, setup.root_file_lines)
    included_file = file_with_lines(included_file_name, setup.included_file_lines)
    arrangement = Arrangement(setup.sections_conf,
                              DirContents([root_file, included_file]),
                              Path(root_file_name))
    expectation = Expectation(matches_document(setup.expected_doc))
    # ACT & ASSERT #
    check(put, arrangement, expectation)


SECTION_1_AND_2_WITHOUT_DEFAULT = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_2_NAME)
                         ),
])

SECTION_1_AND_2_WITH_SECTION_1_AS_DEFAULT = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_2_NAME)
                         ),
],
    default_section_name=SECTION_1_NAME)
