import unittest
from typing import Sequence

from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node, Detail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, \
    MessageBuilder
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions


def matches_node_renderer(rendered_node: Assertion[Node] = described_tree_assertions.matches_node()
                          ) -> Assertion[NodeRenderer]:
    return _MatchesNodeRendererAssertion(rendered_node)


class _MatchesNodeRendererAssertion(AssertionBase[NodeRenderer]):
    def __init__(self,
                 rendered_node: Assertion[Node]):
        self._rendered_node = rendered_node

    def _apply(self,
               put: unittest.TestCase,
               value: NodeRenderer,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             NodeRenderer,
                             message_builder.apply('object type'))

        rendered_node = value.render()

        self._rendered_node.apply(put,
                                  rendered_node,
                                  message_builder.for_sub_component('rendered node'))


def matches_details_renderer(
        rendered_details: Assertion[Sequence[Detail]]
        = asrt.is_sequence_of(described_tree_assertions.is_any_detail())
) -> Assertion[DetailsRenderer]:
    return _MatchesDetailsRendererAssertion(rendered_details)


class _MatchesDetailsRendererAssertion(AssertionBase[DetailsRenderer]):
    def __init__(self, rendered_details: Assertion[Sequence[Detail]]):
        self._rendered_details = rendered_details

    def _apply(self,
               put: unittest.TestCase,
               value: DetailsRenderer,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             DetailsRenderer,
                             message_builder.apply('object type'))

        rendered_details = value.render()

        self._rendered_details.apply(put,
                                     rendered_details,
                                     message_builder.for_sub_component('rendered details'))
