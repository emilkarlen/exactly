import unittest
from typing import Sequence, Optional

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, Document, \
    ElementProperties, LineObject, PreFormattedStringLineObject, StringLineObject, StringLinesObject, \
    PLAIN_ELEMENT_PROPERTIES, LineObjectVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, T, MessageBuilder


def matches_element_properties(
        indented: ValueAssertion[bool] = asrt.anything_goes(),
        color: ValueAssertion[Optional[ForegroundColor]] = asrt.anything_goes()) -> ValueAssertion[ElementProperties]:
    return asrt.is_instance_with__many(ElementProperties,
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
    return asrt.is_instance_with__many(MajorBlock, [
        asrt.sub_component(
            'minor blocks',
            MajorBlock.parts.fget,
            asrt.and_([
                asrt.is_sequence_of(matches_minor_block(asrt.anything_goes())),
                minor_blocks,
            ]),
        ),
        asrt.sub_component(
            'properties',
            MajorBlock.properties.fget,
            properties,
        ),
    ])


def matches_major_block__w_plain_properties(minor_blocks: ValueAssertion[Sequence[MinorBlock]],
                                            ) -> ValueAssertion[MajorBlock]:
    return matches_major_block(
        minor_blocks=minor_blocks,
        properties=equals_element_properties(PLAIN_ELEMENT_PROPERTIES),
    )


def matches_minor_block(line_elements: ValueAssertion[Sequence[LineElement]],
                        properties: ValueAssertion[ElementProperties] = matches_element_properties()
                        ) -> ValueAssertion[MinorBlock]:
    return asrt.is_instance_with__many(MinorBlock, [
        asrt.sub_component(
            'line elements',
            MinorBlock.parts.fget,
            asrt.and_([
                asrt.is_sequence_of(matches_line_element(asrt.anything_goes())),
                line_elements,
            ]),
        ),
        asrt.sub_component(
            'properties',
            MinorBlock.properties.fget,
            properties,
        ),
    ])


def matches_minor_block__w_plain_properties(line_elements: ValueAssertion[Sequence[LineElement]],
                                            ) -> ValueAssertion[MinorBlock]:
    return matches_minor_block(
        line_elements=line_elements,
        properties=equals_element_properties(PLAIN_ELEMENT_PROPERTIES),
    )


def matches_line_element(line_object: ValueAssertion[LineObject],
                         properties: ValueAssertion[ElementProperties] = matches_element_properties()
                         ) -> ValueAssertion[LineElement]:
    return asrt.is_instance_with__many(LineElement, [
        asrt.sub_component(
            'line object',
            LineElement.line_object.fget,
            asrt.is_instance_with(LineObject, line_object),
        ),
        asrt.sub_component(
            'properties',
            LineElement.properties.fget,
            properties,
        ),
    ])


def matches_line_element__w_plain_properties(line_object: ValueAssertion[LineObject]
                                             ) -> ValueAssertion[LineElement]:
    return matches_line_element(
        line_object=line_object,
        properties=equals_element_properties(PLAIN_ELEMENT_PROPERTIES)
    )


def is_pre_formatted_string(string: ValueAssertion[str] = asrt.anything_goes(),
                            string_is_line_ended: ValueAssertion[bool] = asrt.anything_goes()
                            ) -> ValueAssertion[LineObject]:
    return asrt.is_instance_with__many(
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
    return asrt.is_instance_with__many(
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


def is_string__not_line_ended(string: ValueAssertion[str] = asrt.anything_goes(),
                              ) -> ValueAssertion[LineObject]:
    return is_string(
        string,
        string_is_line_ended=asrt.equals(False),
    )


def is_string_lines(strings: ValueAssertion[Sequence[str]] = asrt.anything_goes(),
                    ) -> ValueAssertion[LineObject]:
    return asrt.is_instance_with__many(
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


def is_any_line_object() -> ValueAssertion[LineObject]:
    return _IS_ANY_LINE_OBJECT


class _LineObjectChecker(LineObjectVisitor[unittest.TestCase, None]):
    def visit_pre_formatted(self, put: unittest.TestCase, x: PreFormattedStringLineObject) -> None:
        is_pre_formatted_string().apply_without_message(put, x)

    def visit_string(self, put: unittest.TestCase, x: StringLineObject) -> None:
        is_string().apply_without_message(put, x)

    def visit_string_lines(self, put: unittest.TestCase, x: StringLinesObject) -> None:
        is_string_lines().apply_without_message(put, x)


class _IsAnyLineObject(asrt.ValueAssertionBase[LineObject]):
    _LINE_OBJECT_CHECKER = _LineObjectChecker()

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             LineObject,
                             message_builder.apply('object type'))
        assert isinstance(value, LineObject)
        self._is_known_sub_class(put, value, message_builder)

        value.accept(self._LINE_OBJECT_CHECKER, put)

    def _is_known_sub_class(self,
                            put: unittest.TestCase,
                            value: LineObject,
                            message_builder: MessageBuilder):
        if isinstance(value, PreFormattedStringLineObject):
            return
        if isinstance(value, StringLineObject):
            return
        if isinstance(value, StringLinesObject):
            return
        msg = 'Not a know sub class of {}: {}'.format(LineObject, value)
        put.fail(message_builder.apply(msg))


_IS_ANY_LINE_OBJECT = _IsAnyLineObject()
