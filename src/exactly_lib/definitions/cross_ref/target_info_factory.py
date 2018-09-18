from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure import core


class TheTargetInfoFactory(TargetInfoFactory):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def root(self, presentation: core.StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceId(self.prefix))

    def sub_factory(self, local_name: str) -> TargetInfoFactory:
        return sub_component_factory(local_name, self)


def root_factory() -> TargetInfoFactory:
    return TheTargetInfoFactory('')


def sub_component_factory(local_name: str,
                          root: TheTargetInfoFactory) -> TargetInfoFactory:
    if not root.prefix:
        prefix = local_name
    else:
        prefix = root.prefix + _COMPONENT_SEPARATOR + local_name
    return TheTargetInfoFactory(prefix)


_COMPONENT_SEPARATOR = '.'
