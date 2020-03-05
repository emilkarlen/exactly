import unittest
from typing import Callable, TypeVar

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.description import LogicValueDescription, DescriptionVisitor, DetailsDescription, \
    NodeDescription
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_ddv
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_system.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions

PRIMITIVE = TypeVar('PRIMITIVE')


def matches_logic_ddv(resolved_value: Callable[[Tcds], ValueAssertion[PRIMITIVE]],
                      tcds: Tcds = fake_tcds()) -> ValueAssertion[LogicDdv[PRIMITIVE]]:
    return asrt.is_instance_with__many(
        LogicDdv,
        [
            asrt.sub_component(
                'description',
                _get_description,
                asrt.is_instance_with(LogicValueDescription, _IsValidDescription()),

            ),
            asrt_ddv.matches_dir_dependent_value__with_adv(resolved_value, tcds),
        ])


def _get_description(ddv: LogicDdv) -> LogicValueDescription:
    return ddv.description()


class _IsValidDescription(ValueAssertionBase[LogicValueDescription]):
    def _apply(self,
               put: unittest.TestCase,
               value: LogicValueDescription,
               message_builder: MessageBuilder,
               ):
        value.accept(_IsValidDescriptionChecker(put, message_builder))


class _IsValidDescriptionChecker(DescriptionVisitor[None]):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 ):
        self._put = put
        self._message_builder = message_builder

    def visit_node(self, description: NodeDescription) -> None:
        assertion = asrt_trace_rendering.matches_node_renderer()
        assertion.apply(self._put,
                        description.structure(),
                        self._message_builder
                        )

    def visit_details(self, description: DetailsDescription) -> None:
        assertion = asrt.is_sequence_of(described_tree_assertions.is_any_detail())

        actual_details = description.details().render()

        assertion.apply(self._put, actual_details, self._message_builder)
