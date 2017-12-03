from exactly_lib.help_texts.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CustomTargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure import core


class TheCustomTargetInfoFactory(CustomTargetInfoFactory):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def root(self, presentation: core.StringText) -> TargetInfo:
        return TargetInfo(presentation,
                          CustomCrossReferenceId(self.prefix))

    def sub_factory(self, local_name: str) -> CustomTargetInfoFactory:
        return sub_component_factory(local_name, self)


def root_factory() -> CustomTargetInfoFactory:
    return TheCustomTargetInfoFactory('')


def sub_component_factory(local_name: str,
                          root: TheCustomTargetInfoFactory) -> CustomTargetInfoFactory:
    if not root.prefix:
        prefix = local_name
    else:
        prefix = root.prefix + _COMPONENT_SEPARATOR + local_name
    return TheCustomTargetInfoFactory(prefix)


_COMPONENT_SEPARATOR = '.'
