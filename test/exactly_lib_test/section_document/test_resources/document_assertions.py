import pathlib
from typing import Sequence, Dict

from exactly_lib.section_document import model
from exactly_lib.section_document.model import InstructionInfo, ElementType
from exactly_lib.section_document.section_element_parser import ParsedSectionElement, ParsedInstruction, \
    ParsedNonInstructionElement, ParsedFileInclusionDirective
from exactly_lib.util import line_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def matches_instruction(source: asrt.ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
                        instruction_info: asrt.ValueAssertion[InstructionInfo] = asrt.anything_goes(),
                        ) -> asrt.ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedInstruction,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        ParsedInstruction.source.fget,
                                                        source),
                                     asrt.sub_component('instruction_info',
                                                        ParsedInstruction.instruction_info.fget,
                                                        instruction_info),
                                 ]))


def matches_non_instruction(source: asrt.ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
                            element_type: asrt.ValueAssertion[ElementType] = asrt.anything_goes(),
                            ) -> asrt.ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedNonInstructionElement,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        ParsedNonInstructionElement.source.fget,
                                                        source),
                                     asrt.sub_component('element_type',
                                                        ParsedNonInstructionElement.element_type.fget,
                                                        element_type),
                                 ]))


def equals_non_instruction(expected: ParsedNonInstructionElement) -> asrt.ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(expected.source),
                                   asrt.equals(expected.element_type))


def equals_empty_element(source: line_source.LineSequence) -> asrt.ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(source),
                                   asrt.equals(ElementType.EMPTY))


def equals_comment_element(source: line_source.LineSequence) -> asrt.ValueAssertion[ParsedSectionElement]:
    return matches_non_instruction(equals_line_sequence(source),
                                   asrt.equals(ElementType.COMMENT))


def matches_file_inclusion_directive(
        source: asrt.ValueAssertion[line_source.LineSequence] = asrt.anything_goes(),
        files_to_include: asrt.ValueAssertion[Sequence[pathlib.Path]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[ParsedSectionElement]:
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
                                    ) -> asrt.ValueAssertion[ParsedSectionElement]:
    return matches_file_inclusion_directive(equals_line_sequence(expected.source),
                                            asrt.equals(expected.files_to_include))


def doc_to_dict(doc: model.Document) -> Dict[str, Sequence[model.SectionContentElement]]:
    return {section: doc.section_2_elements[section].elements
            for section in doc.section}


def matches_document(expected: Dict[str, Sequence[asrt.ValueAssertion[model.SectionContentElement]]]
                     ) -> asrt.ValueAssertion[model.Document]:
    expected_section_2_assertion = {section: asrt.matches_sequence(expected[section])
                                    for section in expected.keys()}

    assertion_on_dict = asrt.matches_dict(expected_section_2_assertion)
    return asrt.on_transformed(doc_to_dict, assertion_on_dict)
