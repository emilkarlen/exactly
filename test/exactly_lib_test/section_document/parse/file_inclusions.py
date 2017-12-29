import unittest
from pathlib import Path

from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util.line_source import SourceLocation, single_line_sequence
from exactly_lib_test.section_document.parse.test_resources_for_parse_file import SECTION_1_NAME, \
    ARBITRARY_INSTRUCTION_SOURCE_LINE, NO_FILE_INCLUSIONS, Expectation, check, \
    matches_file_access_error, std_conf_arrangement, is_file_access_error, check_and_expect_exception, inclusion_of_file
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
