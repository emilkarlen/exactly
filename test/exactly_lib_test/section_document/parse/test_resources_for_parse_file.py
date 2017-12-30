import pathlib
import unittest
from pathlib import Path
from typing import Dict, Sequence

from exactly_lib.section_document.document_parser import SectionsConfiguration, SectionElementParser, \
    SectionConfiguration, parse
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.model import InstructionInfo, SectionContentElement
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedSectionElement, new_empty_element, \
    ParsedInstruction, ParsedFileInclusionDirective
from exactly_lib.util.line_source import SourceLocation
from exactly_lib_test.section_document.parse.test_resources import consume_current_line_and_return_it_as_line_sequence, \
    matches_document
from exactly_lib_test.section_document.test_resources.section_contents_elements import InstructionInSection
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_source_location_sequence

INCLUDE_DIRECTIVE_NAME = 'include'
SECTION_1_NAME = 'section1'
SECTION_2_NAME = 'section2'
ARBITRARY_INSTRUCTION_SOURCE_LINE = 'instruction source line'
NO_FILE_INCLUSIONS = []


def inclusion_of_file(file_name: str) -> str:
    return INCLUDE_DIRECTIVE_NAME + ' ' + file_name


class SectionElementParserForInstructionAndInclusionLines(SectionElementParser):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def parse(self,
              source: ParseSource,
              element_builder: SectionContentElementBuilder) -> ParsedSectionElement:
        current_line = source.current_line_text
        consumed_source = consume_current_line_and_return_it_as_line_sequence(source)
        if current_line.isspace():
            return new_empty_element(consumed_source)
        current_line_parts = current_line.split()
        if current_line_parts[0] == INCLUDE_DIRECTIVE_NAME:
            paths_to_include = [
                pathlib.Path(file_name)
                for file_name in current_line_parts[1:]
            ]
            return ParsedFileInclusionDirective(consumed_source, paths_to_include)
        else:
            return ParsedInstruction(consumed_source,
                                     InstructionInfo(InstructionInSection(self._section_name)))


SECTIONS_CONFIGURATION = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_2_NAME)
                         ),
])


class Arrangement:
    def __init__(self,
                 sections_configuration: SectionsConfiguration,
                 cwd_dir_contents: DirContents,
                 root_file: Path):
        self.sections_configuration = sections_configuration
        self.cwd_dir_contents = cwd_dir_contents
        self.root_file = root_file


def std_conf_arrangement(cwd_dir_contents: DirContents,
                         root_file: Path) -> Arrangement:
    return Arrangement(SECTIONS_CONFIGURATION, cwd_dir_contents, root_file)


class Expectation:
    def __init__(self, document: Dict[str, Sequence[asrt.ValueAssertion[SectionContentElement]]]):
        self.document = document


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    # ARRANGE #
    with tmp_dir_as_cwd(arrangement.cwd_dir_contents):
        # ACT #
        actual = parse(arrangement.sections_configuration, arrangement.root_file)
        # ASSERT #
        matches_document(expectation.document).apply_without_message(put, actual)


def is_file_access_error(expected: asrt.ValueAssertion[FileAccessError]) -> asrt.ValueAssertion[Exception]:
    return asrt.is_instance_with(FileAccessError, expected)


def matches_file_access_error(erroneous_path: Path,
                              location_path: Sequence[SourceLocation]) -> asrt.ValueAssertion[FileAccessError]:
    return asrt.and_([
        asrt.sub_component('erroneous_path',
                           FileAccessError.erroneous_path.fget,
                           asrt.equals(erroneous_path)),
        asrt.sub_component('message',
                           FileAccessError.message.fget,
                           asrt.is_not_none),
        asrt.sub_component('location_path',
                           FileAccessError.location_path.fget,
                           equals_source_location_sequence(location_path)),
    ])


def check_and_expect_exception(put: unittest.TestCase,
                               arrangement: Arrangement,
                               expected_exception: asrt.ValueAssertion[Exception]):
    with tmp_dir_as_cwd(arrangement.cwd_dir_contents):
        with put.assertRaises(Exception) as cm:
            # ACT & ASSERT #
            parse(arrangement.sections_configuration, arrangement.root_file)
        expected_exception.apply_with_message(put, cm.exception, 'Exception')
