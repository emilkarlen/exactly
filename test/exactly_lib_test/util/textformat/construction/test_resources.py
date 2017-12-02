from exactly_lib.util.textformat.construction.section_hierarchy import CustomTargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure.core import StringText, CrossReferenceTarget
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


class CustomTargetInfoFactoryTestImpl(CustomTargetInfoFactory):
    def __init__(self, components: list):
        self._components = components

    def sub_factory(self, local_name: str):
        return CustomTargetInfoFactoryTestImpl(self._components + [local_name])

    def root(self, presentation: StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceTargetTestImpl('.'.join(self._components)))
