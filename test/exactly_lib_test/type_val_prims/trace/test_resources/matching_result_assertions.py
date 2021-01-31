from typing import Sequence

from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Detail, Node
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree, \
    rendering_assertions as asrt_trace_rendering


def matches(value: Assertion[bool] = asrt.is_instance(bool),
            trace: Assertion[NodeRenderer[bool]] =
            asrt_trace_rendering.matches_node_renderer()) -> Assertion[MatchingResult]:
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


def matches_value(expected_value: bool) -> Assertion[MatchingResult]:
    return matches_value__w_header(asrt.equals(expected_value),
                                   asrt.anything_goes())


def matches_value__w_header(value: Assertion[bool],
                            header: Assertion[str],
                            details: Assertion[Sequence[Detail]] = asrt.anything_goes(),
                            children: Assertion[Sequence[Node]] = asrt.anything_goes(),
                            ) -> Assertion[MatchingResult]:
    return matches(
        value=value,
        trace=asrt_trace_rendering.matches_node_renderer(
            asrt_d_tree.matches_node(
                header=header,
                data=value,
                details=details,
                children=children
            ),
        )
    )
