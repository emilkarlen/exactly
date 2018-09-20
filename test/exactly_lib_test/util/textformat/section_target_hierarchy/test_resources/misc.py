from typing import List

from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNodeEnvironment
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib_test.util.textformat.constructor.test_resources import CustomCrossReferenceTargetTestImpl

TEST_NODE_ENVIRONMENT = SectionItemNodeEnvironment(set())


class TargetInfoFactoryTestImpl(TargetInfoFactory):
    def __init__(self, components: List[str]):
        self._components = components

    def sub_factory(self, local_name: str) -> TargetInfoFactory:
        return TargetInfoFactoryTestImpl(self._components + [local_name])

    def root(self, presentation: StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceTargetTestImpl('.'.join(self._components)))


class ConstantTargetInfoFactoryTestImpl(TargetInfoFactory):
    def __init__(self, constant: CustomCrossReferenceTargetTestImpl):
        self._constant = constant

    def sub_factory(self, local_name: str) -> TargetInfoFactory:
        return ConstantTargetInfoFactoryTestImpl(self._constant)

    def root(self, presentation: StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          self._constant)
