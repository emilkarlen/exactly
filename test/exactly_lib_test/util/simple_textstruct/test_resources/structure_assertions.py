from typing import Sequence, Optional

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, Document, \
    ElementProperties, LineObject, PreFormattedStringLineObject, StringLineObject, StringLinesObject
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_element_properties(
        indented: ValueAssertion[bool] = asrt.anything_goes(),
        color: ValueAssertion[Optional[ForegroundColor]] = asrt.anything_goes()) -> ValueAssertion[ElementProperties]:
    return asrt.is_instance_with_many(ElementProperties,
                                      [
                                          asrt.sub_component('indented',
                                                             ElementProperties.indented.fget,
                                                             asrt.is_instance_with(bool, indented)
                                                             ),
                                          asrt.sub_component('color',
                                                             ElementProperties.color.fget,
                                                             asrt.is_none_or_instance_with(ForegroundColor, color)
                                                             ),
                                      ])


def equals_element_properties(expected: ElementProperties) -> ValueAssertion[ElementProperties]:
    return matches_element_properties(
        indented=asrt.equals(expected.indented),
        color=asrt.equals(expected.color)
    )


def matches_document(major_blocks: ValueAssertion[Sequence[MajorBlock]]) -> ValueAssertion[Document]:
    return asrt.is_instance_with(Document,
                                 asrt.sub_component(
                                     'major blocks',
                                     Document.blocks.fget,
                                     major_blocks
                                 )
                                 )


def matches_major_block(minor_blocks: ValueAssertion[Sequence[MinorBlock]],
                        properties: ValueAssertion[ElementProperties] = matches_element_properties()
                        ) -> ValueAssertion[MajorBlock]:
    return asrt.is_instance_with_many(MajorBlock, [
        asrt.sub_component(
            'minor blocks',
            MajorBlock.parts.fget,
            minor_blocks
        ),
        asrt.sub_component(
            'properties',
            MajorBlock.properties.fget,
            properties,
        ),
    ])


def matches_minor_block(line_elements: ValueAssertion[Sequence[LineElement]],
                        properties: ValueAssertion[ElementProperties] = matches_element_properties()
                        ) -> ValueAssertion[MinorBlock]:
    return asrt.is_instance_with_many(MinorBlock, [
        asrt.sub_component(
            'line elements',
            MinorBlock.parts.fget,
            line_elements
        ),
        asrt.sub_component(
            'properties',
            MinorBlock.properties.fget,
            properties,
        ),
    ])


def matches_line_element(line_object: ValueAssertion[LineObject],
                         properties: ValueAssertion[ElementProperties] = matches_element_properties()
                         ) -> ValueAssertion[LineElement]:
    return asrt.is_instance_with_many(LineElement, [
        asrt.sub_component(
            'line object',
            LineElement.line_object.fget,
            line_object
        ),
        asrt.sub_component(
            'properties',
            LineElement.properties.fget,
            properties,
        ),
    ])


def is_pre_formatted_string(string: ValueAssertion[str] = asrt.anything_goes(),
                            string_is_line_ended: ValueAssertion[bool] = asrt.anything_goes()
                            ) -> ValueAssertion[LineObject]:
    return asrt.is_instance_with_many(
        PreFormattedStringLineObject,
        [
            asrt.sub_component('string',
                               PreFormattedStringLineObject.string.fget,
                               asrt.is_instance_with(str, string)
                               ),
            asrt.sub_component('string_is_line_ended',
                               PreFormattedStringLineObject.string_is_line_ended.fget,
                               asrt.is_instance_with(bool, string_is_line_ended)
                               ),
        ],
    )


def is_string(string: ValueAssertion[str] = asrt.anything_goes(),
              string_is_line_ended: ValueAssertion[bool] = asrt.anything_goes()
              ) -> ValueAssertion[LineObject]:
    return asrt.is_instance_with_many(
        StringLineObject,
        [
            asrt.sub_component('string',
                               StringLineObject.string.fget,
                               asrt.is_instance_with(str, string)
                               ),
            asrt.sub_component('string_is_line_ended',
                               StringLineObject.string_is_line_ended.fget,
                               asrt.is_instance_with(bool, string_is_line_ended)
                               ),
        ],
    )


def is_string_lines(strings: ValueAssertion[Sequence[str]] = asrt.anything_goes(),
                    ) -> ValueAssertion[LineObject]:
    return asrt.is_instance_with_many(
        StringLinesObject,
        [
            asrt.sub_component('strings',
                               StringLinesObject.strings.fget,
                               asrt.and_([
                                   asrt.is_sequence_of(asrt.is_instance(str)),
                                   strings
                               ])),
        ],
    )
