import unittest
from pathlib import Path, PosixPath
from typing import List, Dict, Sequence

from exactly_lib.section_document.document_parser import SectionConfiguration, SectionsConfiguration
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.model import SectionContentElement
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.line_source import SourceLocation, single_line_sequence
from exactly_lib_test.section_document.parse.test_resources_for_parse_file import SECTION_1_NAME, \
    ARBITRARY_INSTRUCTION_SOURCE_LINE, NO_FILE_INCLUSIONS, Expectation, check, \
    matches_file_access_error, std_conf_arrangement, is_file_access_error, check_and_expect_exception, \
    inclusion_of_file, SectionElementParserForInstructionAndInclusionLines, SECTION_2_NAME, Arrangement, \
    is_file_source_error, matches_file_source_error
from exactly_lib_test.section_document.test_resources.section_contents_elements import \
    equals_instruction_without_description
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, sym_link, empty_file, \
    file_with_lines, empty_dir_contents, add_dir_contents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileAccessErrorShouldBeRaisedWhenFileIsInvalid),
        unittest.makeSuite(TestRootFileWithoutInclusions),
        unittest.makeSuite(TestRootFileWithInclusions),
        unittest.makeSuite(TestCombinationOfDocuments),
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


class TestRootFileWithoutInclusions(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        file_name = 'source-file-name'
        source_file_path = Path(file_name)
        # ACT & ASSERT #
        check(self,
              std_conf_arrangement(DirContents([empty_file(file_name)]),
                                   source_file_path),
              Expectation({}))

    def test_single_instruction(self):
        # ARRANGE #
        source_lines = [
            section_header(SECTION_1_NAME),
            ARBITRARY_INSTRUCTION_SOURCE_LINE,
        ]
        source_file = file_with_lines('source-file.txt', source_lines)
        source_file_path = Path(source_file.file_name)
        # ACT & ASSERT #
        check(self,
              std_conf_arrangement(DirContents([source_file]),
                                   source_file_path),
              Expectation({
                  SECTION_1_NAME: [
                      equals_instruction_without_description(2,
                                                             ARBITRARY_INSTRUCTION_SOURCE_LINE,
                                                             SECTION_1_NAME,
                                                             source_file_path,
                                                             NO_FILE_INCLUSIONS)
                  ]
              })
              )


class TestRootFileWithInclusions(unittest.TestCase):
    def test_inclusion_directive_SHOULD_not_be_allowed_before_section_declaration_when_there_is_no_default_section(
            self):
        # ARRANGE #
        included_file_lines = [
            section_header(SECTION_1_NAME),
            ARBITRARY_INSTRUCTION_SOURCE_LINE,
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
                 root_file_lines: List[str],
                 included_file_lines: List[str],
                 expected_doc: Dict[str, Sequence[asrt.ValueAssertion[SectionContentElement]]]
                 ):
        self.root_file_lines = root_file_lines
        self.included_file_lines = included_file_lines
        self.expected_doc = expected_doc


class TestCombinationOfDocuments(unittest.TestCase):
    def _check(self):
        pass

    def test_combination_of_instruction_from_root_and_included_file(self):
        # ARRANGE #
        root_file_name = 'root.src'
        root_file_path = Path(root_file_name)

        included_file_name = 'included.src'
        included_file_path = Path(included_file_name)

        instruction_1_in_included_file = 'instruction 1 in included file'
        instruction_2_in_included_file = 'instruction 2 in included file'
        instruction_1_in_root_file = 'instruction 1 in root file'
        instruction_2_in_root_file = 'instruction 2 in root file'

        cases = [
            NameAndValue(
                '0 instr in root, 1 instr in included',
                SingleFileInclusionCheckSetup(
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
                '1 instr in root, 1 instr in included (after root) /same section',
                SingleFileInclusionCheckSetup(
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
            root_file = file_with_lines(root_file_name, setup.root_file_lines)
            included_file = file_with_lines(included_file_name, setup.included_file_lines)
            arrangement = Arrangement(SECTION_1_AND_2_WITHOUT_DEFAULT,
                                      DirContents([root_file, included_file]),
                                      root_file_path)
            expectation = Expectation(setup.expected_doc)
            with self.subTest(nav.name):
                # ACT & ASSERT #
                check(self, arrangement, expectation)


SECTION_1_AND_2_WITHOUT_DEFAULT = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_2_NAME)
                         ),
])
