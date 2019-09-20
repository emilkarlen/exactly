import unittest
from typing import Sequence, TypeVar, Generic

from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def is_renderer_of_major_blocks(parts: ValueAssertion[Sequence[MajorBlock]] = asrt.anything_goes()
                                ) -> ValueAssertion[SequenceRenderer[MajorBlock]]:
    return _IsSequenceRenderer(_type_sanity_of_sequence_of_major_blocks(),
                               parts)


def is_renderer_of_minor_blocks(parts: ValueAssertion[Sequence[MinorBlock]] = asrt.anything_goes()
                                ) -> ValueAssertion[SequenceRenderer[MinorBlock]]:
    return _IsSequenceRenderer(_type_sanity_of_sequence_of_minor_blocks(),
                               parts)


def is_renderer_of_line_elements(parts: ValueAssertion[Sequence[LineElement]] = asrt.anything_goes()
                                 ) -> ValueAssertion[SequenceRenderer[LineElement]]:
    return _IsSequenceRenderer(_type_sanity_of_sequence_of_line_elements(),
                               parts)


RENDERED_TYPE = TypeVar('RENDERED_TYPE')


class _IsSequenceRenderer(Generic[RENDERED_TYPE], asrt.ValueAssertionBase[SequenceRenderer[RENDERED_TYPE]]):
    def __init__(self,
                 type_sanity_object_assertion: ValueAssertion[RENDERED_TYPE],
                 custom_assertion: ValueAssertion[RENDERED_TYPE],
                 ):
        self._type_sanity_object_assertion = type_sanity_object_assertion
        self._custom_assertion = custom_assertion

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, SequenceRenderer, 'object type')
        assert isinstance(value, SequenceRenderer)

        rendered_objects = value.render_sequence()

        self._type_sanity_object_assertion.apply(
            put,
            rendered_objects,
            message_builder.for_sub_component('rendered objects')
        )

        self._custom_assertion.apply(
            put,
            rendered_objects,
            message_builder.for_sub_component('rendered objects')
        )


def _type_sanity_of_sequence_of_major_blocks() -> ValueAssertion[Sequence[MajorBlock]]:
    return asrt.is_sequence_of(asrt_struct.matches_major_block(asrt.anything_goes()))


def _type_sanity_of_sequence_of_minor_blocks() -> ValueAssertion[Sequence[MinorBlock]]:
    return asrt.is_sequence_of(asrt_struct.matches_minor_block(asrt.anything_goes()))


def _type_sanity_of_sequence_of_line_elements() -> ValueAssertion[Sequence[LineElement]]:
    return asrt.is_sequence_of(asrt_struct.matches_line_element(asrt.anything_goes()))
