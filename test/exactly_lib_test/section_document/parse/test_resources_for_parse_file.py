import pathlib
import unittest
from pathlib import Path
from typing import Dict, Sequence

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document.document_parser import SectionsConfiguration, SectionElementParser, \
    SectionConfiguration
from exactly_lib.section_document.exceptions import FileAccessError, FileSourceError, new_source_error
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
OK_INSTRUCTION_NAME = 'ok'
SYNTAX_ERROR_INSTRUCTION_NAME = 'error'

SECTION_1_NAME = 'section1'
SECTION_2_NAME = 'section2'
NO_FILE_INCLUSIONS = []


def inclusion_of_file(file_name) -> str:
    if not isinstance(file_name, str):
        file_name = str(file_name)
    return INCLUDE_DIRECTIVE_NAME + ' ' + file_name


def inclusion_of_list_of_files(files: list) -> str:
    return inclusion_of_file(' '.join(files))


def ok_instruction(arg: str) -> str:
    return OK_INSTRUCTION_NAME + ' ' + arg


def syntax_error_instruction(error_message: str) -> str:
    return SYNTAX_ERROR_INSTRUCTION_NAME + ' ' + error_message


ARBITRARY_OK_INSTRUCTION_SOURCE_LINE = ok_instruction('ok instruction line')


class SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SectionElementParser):
    """
    Parse result:
     - line with only space -> EMPTY element
     - line beginning with SYNTAX_ERROR_INSTRUCTION_NAME -> ParseError
     - OK_INSTRUCTION_NAME -> INSTRUCTION element
    """

    def __init__(self, section_name: str):
        self._section_name = section_name

    def parse(self, source: ParseSource) -> ParsedSectionElement:
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
        elif current_line_parts[0] == SYNTAX_ERROR_INSTRUCTION_NAME:
            raise new_source_error(consumed_source, current_line_parts[1])
        elif current_line_parts[0] == OK_INSTRUCTION_NAME:
            return ParsedInstruction(consumed_source,
                                     InstructionInfo(InstructionInSection(self._section_name)))
        else:
            raise ValueError('Unknown source: ' + current_line)


SECTIONS_CONFIGURATION = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_2_NAME)
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
        actual = sut.parse(arrangement.sections_configuration, arrangement.root_file)
        # ASSERT #
        matches_document(expectation.document).apply_without_message(put, actual)


def is_file_source_error(expected: asrt.ValueAssertion[FileSourceError]) -> asrt.ValueAssertion[Exception]:
    return asrt.is_instance_with(FileSourceError, expected)


def matches_file_source_error(maybe_section_name: asrt.ValueAssertion[str],
                              location_path: Sequence[SourceLocation]) -> asrt.ValueAssertion[FileSourceError]:
    return asrt.and_([
        asrt.sub_component('maybe_section_name',
                           FileSourceError.maybe_section_name.fget,
                           maybe_section_name),
        asrt.sub_component('message',
                           FileSourceError.message.fget,
                           asrt.is_not_none),
        asrt.sub_component('location_path',
                           FileSourceError.location_path.fget,
                           equals_source_location_sequence(location_path)),
    ])


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
            sut.parse(arrangement.sections_configuration, arrangement.root_file)
        expected_exception.apply_with_message(put, cm.exception, 'Exception')
