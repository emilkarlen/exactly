from typing import Sequence, Optional

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, Document, \
    ElementProperties, LineObject
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


def matches_line_element(line_objects: ValueAssertion[LineObject],
                         properties: ValueAssertion[ElementProperties] = matches_element_properties()
                         ) -> ValueAssertion[LineElement]:
    return asrt.is_instance_with_many(LineElement, [
        asrt.sub_component(
            'line object',
            LineElement.line_object.fget,
            line_objects
        ),
        asrt.sub_component(
            'properties',
            LineElement.properties.fget,
            properties,
        ),
    ])
