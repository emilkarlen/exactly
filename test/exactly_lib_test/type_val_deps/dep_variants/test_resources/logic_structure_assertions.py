import unittest
from typing import Callable, TypeVar

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.app_env_dep_ddv import LogicDdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_prims.description.logic_description import LogicValueDescription, DescriptionVisitor, \
    DetailsDescription, \
    NodeDescription
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources import dir_dep_value_assertions as asrt_ddv
from exactly_lib_test.type_val_prims.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions

PRIMITIVE = TypeVar('PRIMITIVE')


def matches_logic_ddv(primitive_value: Callable[[TestCaseDs], ValueAssertion],
                      tcds: TestCaseDs = fake_tcds()
                      ) -> ValueAssertion[DirDependentValue]:
    return asrt.is_instance_with__many(
        LogicDdv,
        [
            has_valid_description(),
            has_validator(),
            asrt_ddv.matches_dir_dependent_value__with_adv(primitive_value, tcds),
        ])


def matches_matcher_ddv(primitive_value: Callable[[TestCaseDs], ValueAssertion[MatcherWTrace]],
                        tcds: TestCaseDs = fake_tcds()
                        ) -> ValueAssertion[DirDependentValue]:
    def get_primitive_value_assertion(tcds_: TestCaseDs) -> ValueAssertion:
        return asrt.is_instance_with(MatcherWTrace, primitive_value(tcds_))

    return asrt.is_instance_with__many(
        MatcherDdv,
        [
            has_node_description(),
            has_validator(),
            asrt_ddv.matches_dir_dependent_value__with_adv(get_primitive_value_assertion, tcds),
        ])


def has_valid_description() -> ValueAssertion[LogicDdv[PRIMITIVE]]:
    return asrt.sub_component(
        'description',
        _get_description,
        asrt.is_instance_with(LogicValueDescription, IsValidDescription()),
    )


def has_node_description() -> ValueAssertion[LogicDdv[PRIMITIVE]]:
    return asrt.sub_component(
        'description',
        _get_description,
        asrt.is_instance_with(
            NodeDescription,
            asrt.sub_component(
                'structure',
                _get_node_description_structure,
                asrt_trace_rendering.matches_node_renderer(),
            )
        ),
    )


def has_validator() -> ValueAssertion[LogicDdv[PRIMITIVE]]:
    return asrt.sub_component(
        'validator',
        _get_validator,
        asrt.is_instance(DdvValidator),
    )


def _get_description(ddv: LogicDdv):
    return ddv.description()


def _get_node_description_structure(description: NodeDescription):
    return description.structure()


def _get_validator(ddv: LogicDdv):
    return ddv.validator


class IsValidDescription(ValueAssertionBase[LogicValueDescription]):
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
