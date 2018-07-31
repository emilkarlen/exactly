import pathlib
from typing import List, Sequence

from exactly_lib.section_document import model
from exactly_lib.section_document.model import ElementType
from exactly_lib.util import line_source
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence, equals_source_location, \
    matches_source_location, matches_source_location_path


class InstructionInSection(model.Instruction):
    def __init__(self,
                 section_name: str):
        self._section_name = section_name

    @property
    def section_name(self) -> str:
        return self._section_name


def matches_section_contents_element(
        element_type: ElementType,
        source: asrt.ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
        instruction_info: asrt.ValueAssertion[model.InstructionInfo] = asrt.anything_goes(),
        file_path_rel_referrer: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        file_inclusion_chain: asrt.ValueAssertion[Sequence[line_source.SourceLocation]] = asrt.anything_goes(),
        abs_path_of_dir_containing_file: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
) -> asrt.ValueAssertion[model.SectionContentElement]:
    return asrt.and_([
        asrt.sub_component('element type',
                           model.SectionContentElement.element_type.fget,
                           asrt.equals(element_type)),
        asrt.sub_component('instruction_info',
                           model.SectionContentElement.instruction_info.fget,
                           instruction_info),
        asrt.sub_component('source_location_path',
                           model.SectionContentElement.source_location_path.fget,
                           matches_source_location_path(matches_source_location(source, file_path_rel_referrer),
                                                        file_inclusion_chain)),
        asrt.sub_component('abs_path_of_dir_containing_file',
                           model.SectionContentElement.abs_path_of_dir_containing_file.fget,
                           abs_path_of_dir_containing_file),
    ])


def equals_instruction_in_section(expected: InstructionInSection) -> asrt.ValueAssertion[model.Instruction]:
    return asrt.is_instance_with(InstructionInSection,
                                 asrt.sub_component('section_name',
                                                    InstructionInSection.section_name.fget,
                                                    asrt.equals(expected.section_name)))


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


def equals_file_inclusion_chain(expected: List[line_source.SourceLocation]
                                ) -> asrt.ValueAssertion[Sequence[line_source.SourceLocation]]:
    return asrt.matches_sequence([
        equals_source_location(sl)
        for sl in expected
    ])


def equals_instruction_without_description(line_number: int,
                                           line_text: str,
                                           section_name: str,
                                           file_path_rel_referrer: pathlib.Path,
                                           file_inclusion_chain: List[line_source.SourceLocation],
                                           ) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(
        ElementType.INSTRUCTION,
        equals_line_sequence(single_line_sequence(line_number, line_text)),
        matches_instruction_info_without_description(equals_instruction_in_section(InstructionInSection(section_name))),
        asrt.equals(file_path_rel_referrer),
        equals_file_inclusion_chain(file_inclusion_chain),
    )


def equals_multi_line_instruction_without_description(line_number: int,
                                                      lines: list,
                                                      section_name: str,
                                                      file_path: pathlib.Path,
                                                      file_inclusion_chain: List[line_source.SourceLocation],
                                                      ) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(
        ElementType.INSTRUCTION,
        equals_line_sequence(line_source.LineSequence(line_number,
                                                      tuple(lines))),
        matches_instruction_info_without_description(equals_instruction_in_section(InstructionInSection(section_name))),
        asrt.equals(file_path),
        equals_file_inclusion_chain(file_inclusion_chain),
    )


def equals_empty_element(line_number: int,
                         line_text: str) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(ElementType.EMPTY,
                                            equals_line_sequence(single_line_sequence(line_number, line_text)),
                                            asrt.is_none,
                                            asrt.anything_goes(),
                                            asrt.anything_goes())


def equals_comment_element(line_number: int,
                           line_text: str) -> asrt.ValueAssertion[model.SectionContentElement]:
    return matches_section_contents_element(ElementType.COMMENT,
                                            equals_line_sequence(single_line_sequence(line_number, line_text)),
                                            asrt.is_none,
                                            asrt.anything_goes(),
                                            asrt.anything_goes())
