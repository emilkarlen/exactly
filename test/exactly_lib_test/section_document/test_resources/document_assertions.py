import pathlib
from typing import Sequence, Mapping

from exactly_lib.section_document import model
from exactly_lib.section_document.model import InstructionInfo, ElementType
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement, ParsedInstruction, \
    ParsedNonInstructionElement, ParsedFileInclusionDirective
from exactly_lib.util import line_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def matches_instruction(source: ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
                        instruction_info: ValueAssertion[InstructionInfo] = asrt.anything_goes(),
                        ) -> ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedInstruction,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        ParsedInstruction.source.fget,
                                                        source),
                                     asrt.sub_component('instruction_info',
                                                        ParsedInstruction.instruction_info.fget,
                                                        instruction_info),
                                 ]))


def matches_non_instruction(source: ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
                            element_type: ValueAssertion[ElementType] = asrt.anything_goes(),
                            ) -> ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedNonInstructionElement,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        ParsedNonInstructionElement.source.fget,
                                                        source),
                                     asrt.sub_component('element_type',
                                                        ParsedNonInstructionElement.element_type.fget,
                                                        element_type),
                                 ]))


def equals_non_instruction(expected: ParsedNonInstructionElement) -> ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(expected.source),
                                   asrt.equals(expected.element_type))


def equals_empty_element(source: line_source.LineSequence) -> ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(source),
                                   asrt.equals(ElementType.EMPTY))


def equals_comment_element(source: line_source.LineSequence) -> ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(source),
                                   asrt.equals(ElementType.COMMENT))


def matches_file_inclusion_directive(
        source: ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
        files_to_include: ValueAssertion[Sequence[pathlib.Path]] = asrt.anything_goes(),
) -> ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedFileInclusionDirective,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        ParsedFileInclusionDirective.source.fget,
                                                        source),
                                     asrt.sub_component('files_to_include',
                                                        ParsedFileInclusionDirective.files_to_include.fget,
                                                        files_to_include),
                                 ]))


def equals_file_inclusion_directive(expected: ParsedFileInclusionDirective
                                    ) -> ValueAssertion[ParsedSectionElement]:
    return matches_file_inclusion_directive(equals_line_sequence(expected.source),
                                            asrt.equals(expected.files_to_include))


def doc_to_mapping(doc: model.Document) -> Mapping[str, Sequence[model.SectionContentElement]]:
    return {
        section: doc.section_2_elements[section].elements
        for section in doc.section
    }


def matches_document(expected: Mapping[str, Sequence[ValueAssertion[model.SectionContentElement]]]
                     ) -> ValueAssertion[model.Document]:
    expected_section_2_assertion = {
        section: asrt.matches_sequence(expected[section])
        for section in expected.keys()
    }

    assertion_on_dict = asrt.matches_mapping(expected_section_2_assertion)
    return asrt.on_transformed(doc_to_mapping, assertion_on_dict)
