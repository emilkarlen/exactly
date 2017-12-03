from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget, Text
from exactly_lib.util.textformat.structure.structures import anchor_text


class TargetInfo(tuple):
    def __new__(cls,
                presentation: core.StringText,
                target: core.CrossReferenceTarget):
        return tuple.__new__(cls, (presentation, target))

    @property
    def presentation_text(self) -> core.StringText:
        return self[0]

    @property
    def target(self) -> core.CrossReferenceTarget:
        return self[1]

    def anchor_text(self) -> core.Text:
        return anchor_text(self.presentation_text,
                           self.target)


class TargetInfoNode(tuple):
    def __new__(cls,
                data: TargetInfo,
                children: list):
        """
        :type children: [TargetInfoNode]
        """
        return tuple.__new__(cls, (data, children))

    @property
    def data(self) -> TargetInfo:
        return self[0]

    @property
    def children(self) -> list:
        """
        :rtype [TargetInfoNode]
        """
        return self[1]


def target_info_leaf(ti: TargetInfo) -> TargetInfoNode:
    return TargetInfoNode(ti, [])


class CustomTargetInfoFactory:
    """Build a hierarchical structure of targets to appear in a TOC."""

    def sub(self,
            presentation: str,
            local_target_name: str) -> TargetInfo:
        return self.sub_factory(local_target_name).root(core.StringText(presentation))

    def root(self, presentation: core.StringText) -> TargetInfo:
        raise NotImplementedError('abstract method')

    def sub_factory(self, local_name: str):
        raise NotImplementedError('abstract method')


class NullCustomTargetInfoFactory(CustomTargetInfoFactory):
    """A CustomTargetInfoFactory that build empty CrossReferenceTarget:s"""

    def root(self, presentation: core.StringText) -> TargetInfo:
        return TargetInfo(presentation, CrossReferenceTarget())

    def sub_factory(self, local_name: str):
        return self


class CrossReferenceTextConstructor:
    def apply(self, x: CrossReferenceTarget) -> Text:
        raise NotImplementedError('abstract method')
