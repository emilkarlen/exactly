import unittest
from pathlib import Path

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document import model
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.parse.test_resources import consume_current_line_and_return_it_as_line_sequence, \
    matches_document
from exactly_lib_test.section_document.test_resources.section_contents_elements import InstructionInSection
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, sym_link, empty_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidRootSourceFile),
        unittest.makeSuite(TestEmptyFile),
    ])


INCLUDE_DIRECTIVE_NAME = 'include'

SECTION_1_NAME = 'section1'


class SectionElementParserForInstructionAndInclusionLines(sut.SectionElementParser):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def parse(self,
              source: ParseSource,
              element_builder: SectionContentElementBuilder) -> model.SectionContentElement:
        current_line = source.current_line_text
        consumed_source = consume_current_line_and_return_it_as_line_sequence(source)
        if current_line.isspace():
            return element_builder.new_empty(consumed_source)
        current_line_parts = current_line.split()
        if current_line_parts[0] == INCLUDE_DIRECTIVE_NAME:
            raise NotImplementedError('todo : reporting of include directive')
        else:
            return element_builder.new_instruction(consumed_source,
                                                   InstructionInSection(self._section_name))


SECTIONS_CONFIGURATION = sut.SectionsConfiguration([
    sut.SectionConfiguration(SECTION_1_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_1_NAME)
                             )])


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


class TestEmptyFile(unittest.TestCase):
    def test(self):
        # ARRANGE #
        file_name = 'source-file-name'
        source_file_path = Path(file_name)
        with tmp_dir_as_cwd(DirContents([empty_file(file_name)])):
            # ACT #
            actual = sut.parse(SECTIONS_CONFIGURATION, source_file_path)
            # ASSERT #
            expected = dict()
            matches_document(expected).apply_without_message(self, actual)


def matches_file_access_error(source_file_path: Path) -> asrt.ValueAssertion[FileAccessError]:
    return asrt.and_([
        asrt.sub_component('path',
                           FileAccessError.path.fget,
                           asrt.equals(source_file_path)),
        asrt.sub_component('message',
                           FileAccessError.message.fget,
                           asrt.is_not_none),
    ])
