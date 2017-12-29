import unittest
from pathlib import Path

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.syntax import section_header
from exactly_lib_test.section_document.parse.test_resources_for_parse_file import SECTION_1_NAME, \
    ARBITRARY_INSTRUCTION_SOURCE_LINE, NO_FILE_INCLUSIONS, SECTIONS_CONFIGURATION, Arrangement, Expectation, check, \
    matches_file_access_error
from exactly_lib_test.section_document.test_resources.section_contents_elements import \
    equals_instruction_without_description
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, sym_link, empty_file, file_with_lines
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidRootSourceFile),
        unittest.makeSuite(TestRootFileWithoutInclusions),
    ])


class TestInvalidRootSourceFile(unittest.TestCase):
    def test(self):
        # ARRANGE #
        file_name = 'source-file-name'
        source_file_path = Path(file_name)
        cases = [
            NameAndValue('source file does not exist',
                         DirContents([])
                         ),
            NameAndValue('source file is a directory',
                         DirContents([empty_dir(file_name)])
                         ),
            NameAndValue('symlink to non-existing file',
                         DirContents([sym_link(file_name, 'non-existing-file')])
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                with tmp_dir_as_cwd(nav.value):
                    with self.assertRaises(FileAccessError) as cm:
                        # ACT & ASSERT #
                        sut.parse(SECTIONS_CONFIGURATION, source_file_path)

                    self._assert_matches_file_access_error(source_file_path, cm.exception)

    def _assert_matches_file_access_error(self,
                                          source_file_path: Path,
                                          actual: Exception):
        assert isinstance(actual, FileAccessError)
        matches_file_access_error(source_file_path).apply_without_message(self, actual)


class TestRootFileWithoutInclusions(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        file_name = 'source-file-name'
        source_file_path = Path(file_name)
        # ACT & ASSERT #
        check(self,
              Arrangement(DirContents([empty_file(file_name)]),
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
              Arrangement(DirContents([source_file]),
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


