from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.trace.trace_renderer import NodeRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering


def matches(value: ValueAssertion[bool] = asrt.is_instance(bool),
            trace: ValueAssertion[NodeRenderer[bool]] =
            asrt_trace_rendering.matches_node_renderer()) -> ValueAssertion[MatchingResult]:
    return asrt.is_instance_with__many(MatchingResult,
                                       [
                                          asrt.sub_component('value',
                                                             MatchingResult.value.fget,
                                                             asrt.is_instance_with(bool, value)
                                                             ),
                                          asrt.sub_component('trace',
                                                             MatchingResult.trace.fget,
                                                             asrt.is_instance_with(NodeRenderer, trace)
                                                             ),
                                      ])
