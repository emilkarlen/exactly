import unittest

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.type_system.trace.trace import Node
from exactly_lib.type_system.trace.trace_rendering import NodeRenderer
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_system.trace.test_resources import trace_assertions


def matches_node_renderer(rendered_node: ValueAssertion[Node] = trace_assertions.matches_node(),
                          in_environment: ErrorMessageResolvingEnvironment =
                          ErrorMessageResolvingEnvironment(fake_tcds(), None)
                          ) -> ValueAssertion[NodeRenderer]:
    return _MatchesNodeRendererAssertion(
        rendered_node,
        in_environment,
    )


class _MatchesNodeRendererAssertion(ValueAssertionBase[NodeRenderer]):
    def __init__(self,
                 rendered_node: ValueAssertion[Node],
                 in_environment: ErrorMessageResolvingEnvironment):
        self._rendered_node = rendered_node
        self._in_environment = in_environment

    def _apply(self,
               put: unittest.TestCase,
               value: NodeRenderer,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             NodeRenderer,
                             message_builder.apply('object type'))

        rendered_node = value.render(self._in_environment)

        self._rendered_node.apply(put,
                                  rendered_node,
                                  message_builder.for_sub_component('rendered node'))
