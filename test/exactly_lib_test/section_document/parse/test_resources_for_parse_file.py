import unittest
from pathlib import Path
from typing import Dict, Sequence

from exactly_lib.section_document import document_parser as sut, model
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.exceptions import FileAccessError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.parse.test_resources import consume_current_line_and_return_it_as_line_sequence, \
    matches_document
from exactly_lib_test.section_document.test_resources.section_contents_elements import InstructionInSection
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

INCLUDE_DIRECTIVE_NAME = 'include'
SECTION_1_NAME = 'section1'
SECTION_2_NAME = 'section2'
ARBITRARY_INSTRUCTION_SOURCE_LINE = 'instruction source line'
NO_FILE_INCLUSIONS = []


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
                             ),
    sut.SectionConfiguration(SECTION_2_NAME, SectionElementParserForInstructionAndInclusionLines(SECTION_2_NAME)
                             ),
])


class Arrangement:
    def __init__(self,
                 cwd_dir_contents: DirContents,
                 root_file: Path):
        self.cwd_dir_contents = cwd_dir_contents
        self.root_file = root_file


class Expectation:
    def __init__(self, document: Dict[str, Sequence[asrt.ValueAssertion[model.SectionContentElement]]]):
        self.document = document


def check(put: unittest.TestCase,
          arrangement: Arrangement,
          expectation: Expectation):
    # ARRANGE #
    with tmp_dir_as_cwd(arrangement.cwd_dir_contents):
        # ACT #
        actual = sut.parse(SECTIONS_CONFIGURATION, arrangement.root_file)
        # ASSERT #
        matches_document(expectation.document).apply_without_message(put, actual)


def matches_file_access_error(source_file_path: Path) -> asrt.ValueAssertion[FileAccessError]:
    return asrt.and_([
        asrt.sub_component('path',
                           FileAccessError.path.fget,
                           asrt.equals(source_file_path)),
        asrt.sub_component('message',
                           FileAccessError.message.fget,
                           asrt.is_not_none),
    ])
