import unittest

from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions


def matches_node_renderer(rendered_node: ValueAssertion[Node] = described_tree_assertions.matches_node()
                          ) -> ValueAssertion[NodeRenderer]:
    return _MatchesNodeRendererAssertion(
        rendered_node,
    )


class _MatchesNodeRendererAssertion(ValueAssertionBase[NodeRenderer]):
    def __init__(self,
                 rendered_node: ValueAssertion[Node]):
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
