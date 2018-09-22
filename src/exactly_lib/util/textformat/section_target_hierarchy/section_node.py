from typing import Set, Optional

from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import SectionItemConstructor
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoNode
from exactly_lib.util.textformat.structure import document as doc


class SectionItemNodeEnvironment:
    def __init__(self, toc_section_item_tags: Set[str]):
        self._toc_section_item_tags = toc_section_item_tags

    @property
    def toc_section_item_tags(self) -> Set[str]:
        return self._toc_section_item_tags


class SectionItemNode:
    """
    A node at a fixed position in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy
    (for rendering a TOC),
    and one method for getting the corresponding section-hierarchy
    (for rendering the contents).
    """

    def target_info_node(self) -> Optional[TargetInfoNode]:
        """
        :return: Not None iff the section should appear in the TOC
        """
        raise NotImplementedError()

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionItemConstructor:
        raise NotImplementedError()

    def section_item(self,
                     node_environment: SectionItemNodeEnvironment,
                     construction_environment: ConstructionEnvironment) -> doc.SectionItem:
        """Short cut"""
        return self.section_item_constructor(node_environment).apply(construction_environment)
