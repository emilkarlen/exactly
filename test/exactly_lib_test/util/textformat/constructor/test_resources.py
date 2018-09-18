from typing import List

from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.text import CrossReferenceTextConstructor
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceTarget, Text
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class CustomCrossReferenceTargetTestImpl(CrossReferenceTarget):
    def __init__(self, identifier: str):
        self._identifier = identifier

    @property
    def identifier(self) -> str:
        return self._identifier


def equals_custom_cross_ref_test_impl(expected: CustomCrossReferenceTargetTestImpl) -> asrt.ValueAssertion:
    return asrt.is_instance_with(CustomCrossReferenceTargetTestImpl,
                                 asrt.sub_component('identifier',
                                                    CustomCrossReferenceTargetTestImpl.identifier.fget,
                                                    asrt.equals(expected.identifier)))


class TargetInfoFactoryTestImpl(TargetInfoFactory):
    def __init__(self, components: List[str]):
        self._components = components

    def sub_factory(self, local_name: str) -> TargetInfoFactory:
        return TargetInfoFactoryTestImpl(self._components + [local_name])

    def root(self, presentation: StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceTargetTestImpl('.'.join(self._components)))


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return StringText('Reference to ' + str(x))


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())
