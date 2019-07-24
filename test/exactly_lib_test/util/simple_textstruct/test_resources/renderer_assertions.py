import unittest
from typing import Sequence, TypeVar, Generic

from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def is_renderer_of_major_blocks() -> ValueAssertion[Renderer[Sequence[MajorBlock]]]:
    return _IS_RENDERER_OF_MAJOR_BLOCKS


def is_renderer_of_minor_blocks() -> ValueAssertion[Renderer[Sequence[MinorBlock]]]:
    return _IS_RENDERER_OF_MINOR_BLOCKS


def is_renderer_of_line_elements() -> ValueAssertion[Renderer[Sequence[LineElement]]]:
    return _IS_RENDERER_OF_LINE_ELEMENT


RENDERED_TYPE = TypeVar('RENDERED_TYPE')


class _IsRenderer(Generic[RENDERED_TYPE], asrt.ValueAssertionBase[Renderer[RENDERED_TYPE]]):
    def __init__(self, rendered_object_assertion: ValueAssertion[RENDERED_TYPE]):
        self._rendered_object_assertion = rendered_object_assertion

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, Renderer, 'object type')
        assert isinstance(value, Renderer)

        rendered_object = value.render()

        self._rendered_object_assertion.apply(put,
                                              rendered_object,
                                              message_builder.for_sub_component('rendered object'))


_IS_RENDERER_OF_MAJOR_BLOCKS = _IsRenderer(asrt.is_sequence_of(asrt_struct.matches_major_block(asrt.anything_goes())))

_IS_RENDERER_OF_MINOR_BLOCKS = _IsRenderer(asrt.is_sequence_of(asrt_struct.matches_minor_block(asrt.anything_goes())))

_IS_RENDERER_OF_LINE_ELEMENT = _IsRenderer(asrt.is_sequence_of(asrt_struct.matches_line_element(asrt.anything_goes())))
