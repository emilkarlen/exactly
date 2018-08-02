import unittest
from pathlib import Path, PosixPath, PurePosixPath
from typing import List, Dict, Sequence

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.model import SectionContentElement, ElementType
from exactly_lib.section_document.parsing_configuration import SectionConfiguration, SectionsConfiguration
from exactly_lib.section_document.source_location import SourceLocation
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.section_document.document_parser.test_resources.arrangement_and_expectation import Expectation, \
    check, \
    std_conf_arrangement, check_and_expect_exception, \
    Arrangement
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import SECTION_1_NAME, \
    SECTION_2_NAME, \
    NO_FILE_INCLUSIONS, inclusion_of_file, inclusion_of_list_of_files, ok_instruction, syntax_error_instruction, \
    ARBITRARY_OK_INSTRUCTION_SOURCE_LINE, SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions, \
    UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE
from exactly_lib_test.section_document.document_parser.test_resources.exception_assertions import is_file_source_error, \
    matches_file_source_error, is_file_access_error, matches_file_access_error
from exactly_lib_test.section_document.test_resources.document_assertions import matches_document
from exactly_lib_test.section_document.test_resources.element_assertions import \
    equals_instruction_without_description, matches_section_contents_element, \
    matches_instruction_info_without_description, matches_instruction_with_parse_source_info
from exactly_lib_test.section_document.test_resources.source_location_assertions import equals_source_location_sequence, \
    matches_file_location_info, matches_source_location_info2
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, sym_link, file_with_lines, \
    empty_dir_contents, add_dir_contents, Dir
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileAccessErrorShouldBeRaisedWhenFileIsInvalid),
        unittest.makeSuite(TestDetectionOfSyntaxError),
        unittest.makeSuite(TestSectionSwitching),
        unittest.makeSuite(TestCombinationOfDocuments),
        unittest.makeSuite(TestMultipleInclusionsOfSameFile),
        unittest.makeSuite(TestInclusionFromInclusion),
        unittest.makeSuite(TestSourceLocationInfoGivenToElementParser),
        unittest.makeSuite(TestDetectionOfInclusionCycles),
        unittest.makeSuite(TestAbsPathOfDirContainingFile),
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


class TestDetectionOfSyntaxError(unittest.TestCase):
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

    def test_source_locations_of_file_source_error_when_element_parser_reports_error_by_returning_none(self):
        # ARRANGE #
        setup = SetupWithDoubleInclusionAndIncludedFilesInSubDir(
            source_line_in_included_file_2_or_none_if_file_should_not_exist=
            UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE
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
                                                    UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE),
                               Path(setup.included_file_2.name)),

            ]
        )
        # ACT & ASSERT #
        check_and_expect_exception(self, arrangement,
                                   is_file_source_error(expected_file_source_error))


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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                        file_path_rel_referrer=included_file_path,
                        file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
                                    SourceLocation(
                                        single_line_sequence(2, inclusion_of_list_of_files([included_file_name,
                                                                                            included_file_name])),
                                        root_file_path)
                                ]),
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_1_NAME,
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
                                    SourceLocation(single_line_sequence(2, inclusion_of_file(included_file_name)),
                                                   root_file_path)
                                ]),
                        ],
                        SECTION_2_NAME: [
                            equals_instruction_without_description(
                                1,
                                instruction_in_included_file,
                                SECTION_2_NAME,
                                file_path_rel_referrer=included_file_path,
                                file_inclusion_chain=[
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
                    file_path_rel_referrer=Path(setup.included_file_2.name),
                    file_inclusion_chain=[
                        setup.source_location_of_inclusion_of_file_1_from_root_file,
                        setup.source_location_of_inclusion_of_file_2_from_included_file_1,
                    ]
                ),
                equals_instruction_without_description(
                    2,
                    setup.instruction_in_included_file_1,
                    SECTION_1_NAME,
                    file_path_rel_referrer=Path(setup.sub_dir_of_included_files) / setup.included_file_1.name,
                    file_inclusion_chain=[
                        setup.source_location_of_inclusion_of_file_1_from_root_file,
                    ]
                ),
                equals_instruction_without_description(
                    3,
                    setup.instruction_in_root_file,
                    SECTION_1_NAME,
                    file_path_rel_referrer=setup.root_file_path,
                    file_inclusion_chain=NO_FILE_INCLUSIONS,
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


class TestSourceLocationInfoGivenToElementParser(unittest.TestCase):
    def test(self):
        # ARRANGE #
        sub_dir_name = 'sub-dir'
        sub_dir_path = Path(sub_dir_name)

        file_2_in_sub_dir = file_with_lines('2.src', [
            ok_instruction('2'),
        ])

        file_2_rel_file_1 = sub_dir_path / file_2_in_sub_dir.name
        file_1_in_root_dir = file_with_lines('1.src', [
            ok_instruction('1'),
            inclusion_of_file(file_2_rel_file_1),
        ])

        file_1_rel_file_0 = Path('..') / file_1_in_root_dir.name
        file_0_in_sub_dir = file_with_lines('0.src', [
            ok_instruction('0'),
            inclusion_of_file(file_1_rel_file_0),
        ])

        cwd_dir_contents = DirContents([
            file_1_in_root_dir,
            Dir(sub_dir_name, [
                file_0_in_sub_dir,
                file_2_in_sub_dir,
            ])
        ])
        root_file_path = sub_dir_path / file_0_in_sub_dir.name
        with tmp_dir_as_cwd(cwd_dir_contents) as cwd_path:
            # ACT #
            actual_doc = sut.parse(SECTION_1_WITH_SECTION_1_AS_DEFAULT,
                                   root_file_path)
            # EXPECTATION #
            inclusion_of_file_1_from_file_0 = SourceLocation(
                single_line_sequence(2, inclusion_of_file(file_1_rel_file_0)),
                root_file_path)

            inclusion_of_file_2_from_file_1 = SourceLocation(
                single_line_sequence(2, inclusion_of_file(file_2_rel_file_1)),
                file_1_rel_file_0)

            abs_cwd_path = cwd_path.resolve()
            expected_doc = {
                SECTION_1_NAME: [
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        instruction_info=matches_instruction_info_without_description(
                            matches_instruction_with_parse_source_info(
                                current_source_file=matches_file_location_info(
                                    abs_path_of_dir_containing_root_file=asrt.equals(cwd_path),
                                    file_path_rel_referrer=asrt.equals(root_file_path),
                                    abs_path_of_dir_containing_file=asrt.equals(abs_cwd_path / sub_dir_name),
                                    file_inclusion_chain=asrt.is_empty_sequence,
                                )
                            )
                        ),
                    ),
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        instruction_info=matches_instruction_info_without_description(
                            matches_instruction_with_parse_source_info(
                                current_source_file=matches_file_location_info(
                                    abs_path_of_dir_containing_root_file=asrt.equals(cwd_path),
                                    file_path_rel_referrer=asrt.equals(file_1_rel_file_0),
                                    abs_path_of_dir_containing_file=asrt.equals(
                                        abs_cwd_path / sub_dir_name / Path('..')
                                    ),
                                    file_inclusion_chain=equals_source_location_sequence([
                                        inclusion_of_file_1_from_file_0,
                                    ]),
                                )
                            )
                        ),
                    ),
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        instruction_info=matches_instruction_info_without_description(
                            matches_instruction_with_parse_source_info(
                                current_source_file=matches_file_location_info(
                                    abs_path_of_dir_containing_root_file=asrt.equals(cwd_path),
                                    file_path_rel_referrer=asrt.equals(file_2_rel_file_1),
                                    abs_path_of_dir_containing_file=asrt.equals(
                                        abs_cwd_path / sub_dir_name / Path('..') / sub_dir_name
                                    ),
                                    file_inclusion_chain=equals_source_location_sequence([
                                        inclusion_of_file_1_from_file_0,
                                        inclusion_of_file_2_from_file_1,
                                    ]),
                                )
                            )
                        ),
                    ),
                ],
            }
            assertion_on_doc = matches_document(expected_doc)
            # ASSERT #
            assertion_on_doc.apply_without_message(self, actual_doc)


class TestAbsPathOfDirContainingFile(unittest.TestCase):
    def test(self):
        # ARRANGE #
        sub_dir_name = 'sub-dir'
        sub_dir_path = PurePosixPath(sub_dir_name)
        file_0_in_sub_dir_name = '0.src'
        file_1_in_root_dir_name = '1.src'
        file_2_in_sub_dir_name = '2.src'

        file_2_in_sub_dir = file_with_lines(file_2_in_sub_dir_name, [
            ok_instruction('2'),
        ])
        file_1_in_root_dir = file_with_lines(file_1_in_root_dir_name, [
            ok_instruction('1'),
            inclusion_of_file(sub_dir_path / file_2_in_sub_dir.name),
        ])
        file_0_in_sub_dir = file_with_lines(file_0_in_sub_dir_name, [
            ok_instruction('0'),
            inclusion_of_file(PurePosixPath('..') / file_1_in_root_dir.name),
        ])
        cwd_dir_contents = DirContents([
            file_1_in_root_dir,
            Dir(sub_dir_name, [
                file_0_in_sub_dir,
                file_2_in_sub_dir,
            ])
        ])
        root_file_path = Path(sub_dir_name) / file_0_in_sub_dir.name
        with tmp_dir_as_cwd(cwd_dir_contents) as cwd_path:
            # ACT #
            actual_doc = sut.parse(SECTION_1_WITH_SECTION_1_AS_DEFAULT,
                                   root_file_path)
            # EXPECTATION #
            abs_cwd_path = cwd_path.resolve()
            expected_doc = {
                SECTION_1_NAME: [
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        source_location_info=
                        matches_source_location_info2(
                            abs_path_of_dir_containing_file=
                            asrt.equals(abs_cwd_path / sub_dir_name),
                        )
                    ),
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        source_location_info=
                        matches_source_location_info2(
                            abs_path_of_dir_containing_file=asrt.equals(
                                abs_cwd_path / sub_dir_name / PurePosixPath('..')
                            ),
                        )
                    ),
                    matches_section_contents_element(
                        ElementType.INSTRUCTION,
                        source_location_info=
                        matches_source_location_info2(
                            abs_path_of_dir_containing_file=asrt.equals(
                                abs_cwd_path / sub_dir_name / PurePosixPath('..') / sub_dir_name
                            ),
                        )
                    ),
                ],
            }
            # ASSERT #
            assertion_on_doc = matches_document(expected_doc)
            assertion_on_doc.apply_without_message(self, actual_doc)


class TestDetectionOfInclusionCycles(unittest.TestCase):
    def test_inclusion_of_current_source_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)
        root_file = file_with_lines(root_file_name, [
            inclusion_of_file(root_file_name),
        ])
        cwd_dir_contents = DirContents([root_file])

        arrangement = Arrangement(SECTION_1_AND_2_WITH_SECTION_1_AS_DEFAULT,
                                  cwd_dir_contents,
                                  root_file_path)
        # EXPECTATION #
        expected_exception = is_file_access_error(
            matches_file_access_error(
                erroneous_path=root_file_path,
                location_path=[
                    SourceLocation(single_line_sequence(1, inclusion_of_file(root_file_name)),
                                   root_file_path)
                ]))
        # ACT & ASSERT #
        check_and_expect_exception(self,
                                   arrangement=arrangement,
                                   expected_exception=expected_exception)

    def test_inclusion_of_current_source_file_via_sym_link(self):
        # ARRANGE #
        non_symlink_file_name = 'file.src'
        non_symlink_file_path = Path(non_symlink_file_name)

        symlink_file_name = 'sym-link-to-file.src'
        symlink_file_path = Path(symlink_file_name)

        symlink_file = sym_link(symlink_file_name,
                                non_symlink_file_name)

        cases = [
            NEA('root file is non-symlink file',
                expected=matches_file_access_error(
                    erroneous_path=symlink_file_path,
                    location_path=[
                        SourceLocation(single_line_sequence(1, inclusion_of_file(symlink_file_name)),
                                       non_symlink_file_path)
                    ]),
                actual=Arrangement(SECTION_1_WITH_SECTION_1_AS_DEFAULT,
                                   cwd_dir_contents=DirContents([
                                       file_with_lines(non_symlink_file_name, [
                                           inclusion_of_file(symlink_file_name),
                                       ]),
                                       symlink_file,
                                   ]),
                                   root_file=non_symlink_file_path)
                ),
            NEA('root file is symlink file',
                expected=matches_file_access_error(
                    erroneous_path=non_symlink_file_path,
                    location_path=[
                        SourceLocation(single_line_sequence(1, inclusion_of_file(non_symlink_file_name)),
                                       symlink_file_path)
                    ]),
                actual=Arrangement(SECTION_1_WITH_SECTION_1_AS_DEFAULT,
                                   cwd_dir_contents=DirContents([
                                       file_with_lines(non_symlink_file_name, [
                                           inclusion_of_file(non_symlink_file_name),
                                       ]),
                                       symlink_file,
                                   ]),
                                   root_file=symlink_file_path)
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                # ACT & ASSERT #
                check_and_expect_exception(self,
                                           arrangement=nea.actual,
                                           expected_exception=is_file_access_error(nea.expected))

    def test_distance_gt_1_and_different_rel_path_of_file_included_twice(self):
        # ARRANGE #
        sub_dir_name = 'sub-dir'
        sub_dir_path = PurePosixPath('sub-dir')
        file_in_root_dir_0_name = '0.src'
        file_in_root_dir_1_name = '1.src'
        file_in_sub_dir_2_name = '2.src'
        file_in_sub_dir_3_name = '3.src'
        file_in_sub_dir_4_name = '4.src'

        inclusion_of_file_1_source_code = inclusion_of_file(file_in_root_dir_1_name)
        file_in_root_dir_0 = file_with_lines(file_in_root_dir_0_name, [
            inclusion_of_file_1_source_code,
        ])

        inclusion_of_file_2_source_code = inclusion_of_file(sub_dir_path / file_in_sub_dir_2_name)
        file_in_root_dir_1 = file_with_lines(file_in_root_dir_1_name, [
            inclusion_of_file_2_source_code,
        ])
        inclusion_of_file_3_source_code = inclusion_of_file(file_in_sub_dir_3_name)
        file_in_sub_dir_2 = file_with_lines(file_in_sub_dir_2_name, [
            inclusion_of_file_3_source_code
        ])
        inclusion_of_file_4_source_code = inclusion_of_file(file_in_sub_dir_4_name)
        file_in_sub_dir_3 = file_with_lines(file_in_sub_dir_3_name, [
            inclusion_of_file_4_source_code
        ])

        inclusion_path_that_cause_circle = PurePosixPath('..') / file_in_root_dir_1_name
        inclusion_of_file_1_from_file_4_source_code = inclusion_of_file(inclusion_path_that_cause_circle)
        file_in_sub_dir_4 = file_with_lines(file_in_sub_dir_4_name, [
            inclusion_of_file_1_from_file_4_source_code
        ])

        cwd_dir_contents = DirContents([
            file_in_root_dir_0,
            file_in_root_dir_1,
            Dir(sub_dir_name, [
                file_in_sub_dir_2,
                file_in_sub_dir_3,
                file_in_sub_dir_4,
            ])
        ])
        # EXPECTATION #
        expected_exception = is_file_access_error(
            matches_file_access_error(
                erroneous_path=Path(inclusion_path_that_cause_circle),
                location_path=[
                    SourceLocation(single_line_sequence(1, inclusion_of_file_1_source_code),
                                   Path(file_in_root_dir_0_name)),
                    SourceLocation(single_line_sequence(1, inclusion_of_file_2_source_code),
                                   Path(file_in_root_dir_1_name)),
                    SourceLocation(single_line_sequence(1, inclusion_of_file_3_source_code),
                                   Path(sub_dir_path / file_in_sub_dir_2_name)),
                    SourceLocation(single_line_sequence(1, inclusion_of_file_4_source_code),
                                   Path(file_in_sub_dir_3_name)),
                    SourceLocation(single_line_sequence(1, inclusion_of_file_1_from_file_4_source_code),
                                   Path(file_in_sub_dir_4_name)),
                ])
        )
        arrangement = Arrangement(SECTION_1_WITH_SECTION_1_AS_DEFAULT,
                                  cwd_dir_contents,
                                  Path(file_in_root_dir_0_name))
        # ACT & ASSERT #
        check_and_expect_exception(self,
                                   arrangement=arrangement,
                                   expected_exception=expected_exception)


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

SECTION_1_WITH_SECTION_1_AS_DEFAULT = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_1_NAME)
                         ),
],
    default_section_name=SECTION_1_NAME)
