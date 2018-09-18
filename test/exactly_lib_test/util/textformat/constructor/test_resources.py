from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.text import CrossReferenceTextConstructor
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


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return StringText('Reference to ' + str(x))


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())
