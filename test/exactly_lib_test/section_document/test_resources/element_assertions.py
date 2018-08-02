import pathlib
from typing import List

from exactly_lib.section_document import model
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.source_location import SourceLocation, FileLocationInfo, FileSystemLocationInfo, \
    SourceLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.section_document.test_resources.source_location_assertions import equals_file_inclusion_chain, \
    matches_source_location_info2
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


class InstructionInSection(model.Instruction):
    def __init__(self,
                 section_name: str):
        self._section_name = section_name

    @property
    def section_name(self) -> str:
        return self._section_name


class InstructionInSectionWithParseSourceInfo(InstructionInSection):
    def __init__(self,
                 section_name: str,
                 fs_location_info: FileSystemLocationInfo):
        super().__init__(section_name)
        self._fs_location_info = fs_location_info

    @property
    def fs_location_info(self) -> FileSystemLocationInfo:
        return self._fs_location_info


def matches_section_contents_element(
        element_type: ElementType,
        instruction_info: asrt.ValueAssertion[model.InstructionInfo] = asrt.anything_goes(),
        source_location_info: asrt.ValueAssertion[SourceLocationInfo] = asrt.anything_goes(),
) -> asrt.ValueAssertion[model.SectionContentElement]:
    return asrt.and_([
        asrt.sub_component('element type',
                           model.SectionContentElement.element_type.fget,
                           asrt.equals(element_type)),
        asrt.sub_component('instruction_info',
                           model.SectionContentElement.instruction_info.fget,
                           instruction_info),
        asrt.sub_component('source_location_info',
                           model.SectionContentElement.source_location_info.fget,
                           source_location_info),
    ])


def equals_instruction_in_section(expected: InstructionInSection) -> asrt.ValueAssertion[model.Instruction]:
    return asrt.is_instance_with(InstructionInSection,
                                 asrt.sub_component('section_name',
                                                    InstructionInSection.section_name.fget,
                                                    asrt.equals(expected.section_name)))


def matches_instruction_with_parse_source_info(
        section_name: asrt.ValueAssertion[str] = asrt.anything_goes(),
        current_source_file: asrt.ValueAssertion[FileLocationInfo] = asrt.anything_goes(),
) -> asrt.ValueAssertion[model.Instruction]:
    return asrt.is_instance_with_many(InstructionInSectionWithParseSourceInfo,
                                      [
                                          asrt.sub_component('section_name',
                                                             InstructionInSectionWithParseSourceInfo.section_name.fget,
                                                             section_name),
                                          asrt.sub_component('current_source_file',
                                                             lambda instr: instr.fs_location_info.current_source_file,
                                                             current_source_file),
                                      ])


def matches_instruction_info(assertion_on_description: asrt.ValueAssertion[str],
                             assertion_on_instruction: asrt.ValueAssertion[model.Instruction],
                             ) -> asrt.ValueAssertion[model.InstructionInfo]:
    return asrt.and_([
        asrt.sub_component('description',
                           model.InstructionInfo.description.fget,
                           assertion_on_description),
        asrt.sub_component('instruction',
                           model.InstructionInfo.instruction.fget,
                           assertion_on_instruction),
    ])


def matches_instruction_info_without_description(assertion_on_instruction: asrt.ValueAssertion[model.Instruction],
                                                 ) -> asrt.ValueAssertion[model.InstructionInfo]:
    return matches_instruction_info(assertion_on_description=asrt.is_none,
                                    assertion_on_instruction=assertion_on_instruction)


def equals_instruction_without_description(line_number: int,
                                           line_text: str,
                                           section_name: str,
                                           file_path_rel_referrer: pathlib.Path,
                                           file_inclusion_chain: List[SourceLocation],
                                           ) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(
        ElementType.INSTRUCTION,
        instruction_info=
        matches_instruction_info_without_description(equals_instruction_in_section(InstructionInSection(section_name))),
        source_location_info=
        matches_source_location_info2(
            source=equals_line_sequence(single_line_sequence(line_number, line_text)),
            file_path_rel_referrer=asrt.equals(file_path_rel_referrer),
            file_inclusion_chain=equals_file_inclusion_chain(file_inclusion_chain),
        )
    )


def equals_multi_line_instruction_without_description(line_number: int,
                                                      lines: list,
                                                      section_name: str,
                                                      file_path: pathlib.Path,
                                                      file_inclusion_chain: List[SourceLocation],
                                                      ) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(
        ElementType.INSTRUCTION,
        instruction_info=matches_instruction_info_without_description(
            equals_instruction_in_section(InstructionInSection(section_name))),
        source_location_info=
        matches_source_location_info2(
            source=equals_line_sequence(line_source.LineSequence(line_number,
                                                                 tuple(lines))),
            file_path_rel_referrer=asrt.equals(file_path),
            file_inclusion_chain=equals_file_inclusion_chain(file_inclusion_chain),
        )
    )


def equals_empty_element(line_number: int,
                         line_text: str) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(ElementType.EMPTY,
                                            instruction_info=asrt.is_none,
                                            source_location_info=
                                            matches_source_location_info2(
                                                source=equals_line_sequence(
                                                    single_line_sequence(line_number, line_text)),
                                            )
                                            )


def equals_comment_element(line_number: int,
                           line_text: str) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(ElementType.COMMENT,
                                            instruction_info=asrt.is_none,
                                            source_location_info=
                                            matches_source_location_info2(
                                                source=equals_line_sequence(
                                                    single_line_sequence(line_number, line_text)),
                                            )
                                            )
