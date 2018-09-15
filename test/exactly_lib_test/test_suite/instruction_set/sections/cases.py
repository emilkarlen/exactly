import unittest

from exactly_lib.section_document import parsed_section_element
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_suite.instruction_set.sections import cases as sut
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check, equivalent_source_variants
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, empty_dir, empty_dir_contents
from exactly_lib_test.test_suite.instruction_set.sections.test_resources.file_resolving_test_base import \
    ResolvePathsTestBase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestResolvePaths),
    ])


class TestParse(unittest.TestCase):
    def test_fail_when_invalid_syntax(self):
        test_cases = [
            '',
            '   ',
            'too many tokens',
        ]
        parser = sut.new_parser()
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_succeed_when_valid_syntax(self):
        test_cases = [
            'file-name.ext',
            '**.ext',
            '\'quoted file name ***\'',
        ]
        parser = sut.new_parser()
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                    self.assertIsInstance(actual,
                                          parsed_section_element.ParsedInstruction)
                    self.assertIsInstance(actual.instruction_info.instruction,
                                          sut.CasesSectionInstruction)


class TestResolvePaths(ResolvePathsTestBase):
    def test_single_file_WHEN_argument_is_existing_single_file(self):
        file = empty_file('suite.file')
        self._expect_success(
            contents_dir_contents=DirContents([file]),
            source=file.name,
            expected_contents_rel_contents_dir=[
                file.name_as_path,
            ]
        )

    def test_fail_WHEN_argument_is_non_existing_file(self):
        self._expect_resolving_error(
            contents_dir_contents=empty_dir_contents(),
            source='non-existing.file',
        )

    def test_all_files_in_dir_WHEN_argument_is_glob_including_all_files(self):
        file_1 = empty_file('1-file.ext')
        file_2 = empty_file('2-file.ext')
        self._expect_success(
            contents_dir_contents=DirContents([file_1,
                                               file_2]),
            source='*',
            expected_contents_rel_contents_dir=[
                file_1.name_as_path,
                file_2.name_as_path,
            ]
        )

    def test_fail_WHEN_argument_is_existing_dir(self):
        a_dir = empty_dir('a-dir')
        self._expect_resolving_error(
            contents_dir_contents=DirContents([a_dir]),
            source=a_dir.name,
        )

    def _expected_instruction_class(self):
        return sut.CasesSectionInstruction

    def _parser(self) -> SectionElementParser:
        return sut.new_parser()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
