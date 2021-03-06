import pathlib
from typing import List

from exactly_lib.section_document import model
from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.model import SectionContentElement, Instruction
from exactly_lib.section_document.source_location import SourceLocation, FileLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line, LineSequence
from exactly_lib_test.section_document.test_resources.element_assertions import InstructionInSection

_ELEMENT_BUILDER_WITHOUT_FILE_PATH = SectionContentElementBuilder(FileLocationInfo(pathlib.Path.cwd()))


def new_comment_element(source_line: line_source.Line) -> SectionContentElement:
    return _ELEMENT_BUILDER_WITHOUT_FILE_PATH.new_comment(new_ls_from_line(source_line))


def new_instruction_element(source_line: line_source.Line,
                            instruction: Instruction) -> SectionContentElement:
    return _ELEMENT_BUILDER_WITHOUT_FILE_PATH.new_instruction(new_ls_from_line(source_line),
                                                              instruction,
                                                              None)


def new_ls_from_line(line: Line) -> LineSequence:
    return LineSequence(line.line_number,
                        (line.text,))


def new_comment(line_number: int,
                line_text: str) -> model.SectionContentElement:
    return _ELEMENT_BUILDER_WITHOUT_FILE_PATH.new_comment(line_source.LineSequence(line_number,
                                                                                   (line_text,)))


def new_empty(line_number: int,
              line_text: str) -> model.SectionContentElement:
    return _ELEMENT_BUILDER_WITHOUT_FILE_PATH.new_empty(line_source.LineSequence(line_number,
                                                                                 (line_text,)))


def new_instruction(line_number: int,
                    line_text: str,
                    section_name: str,
                    file_path: pathlib.Path = None,
                    file_inclusion_chain: List[SourceLocation] = ()) -> model.SectionContentElement:
    builder = SectionContentElementBuilder(
        FileLocationInfo(pathlib.Path('/'),
                         file_path,
                         file_inclusion_chain,
                         ))
    return builder.new_instruction(line_source.LineSequence(line_number,
                                                            (line_text,)),
                                   InstructionInSection(section_name))


def _root_path_if_non(path: pathlib.Path) -> pathlib.Path:
    if path is None:
        return pathlib.Path('/')
    else:
        return path
