from typing import Set

from exactly_lib.util.textformat.construction.section_contents.constructor import SectionItemConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode
from exactly_lib.util.textformat.structure import document as doc


class SectionItemNodeEnvironment:
    def __init__(self, toc_section_item_tags: Set[str]):
        self._toc_section_item_tags = toc_section_item_tags

    @property
    def toc_section_item_tags(self) -> Set[str]:
        return self._toc_section_item_tags


class SectionItemNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy
    (for rendering a TOC),
    and one method for getting the corresponding section-hierarchy
    (for rendering the contents).
    """

    def target_info_node(self) -> TargetInfoNode:
        raise NotImplementedError()

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionItemConstructor:
        raise NotImplementedError()

    def section_item(self,
                     node_environment: SectionItemNodeEnvironment,
                     construction_environment: ConstructionEnvironment) -> doc.SectionItem:
        """Short cut"""
        return self.section_item_constructor(node_environment).apply(construction_environment)
