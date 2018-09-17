from typing import Set

from exactly_lib.util.textformat.construction.section_contents.constructor import \
    SectionItemConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode, TargetInfoFactory
from exactly_lib.util.textformat.structure import document as doc


class SectionItemGeneratorEnvironment:
    def __init__(self, toc_section_item_tags: Set[str]):
        self._toc_section_item_tags = toc_section_item_tags

    @property
    def toc_section_item_tags(self) -> Set[str]:
        return self._toc_section_item_tags


class SectionItemGeneratorNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy
    (for rendering a TOC),
    and one method for getting the corresponding section-hierarchy
    (for rendering the contents).
    """

    def target_info_node(self) -> TargetInfoNode:
        raise NotImplementedError()

    def section_item_constructor(self,
                                 generator_environment: SectionItemGeneratorEnvironment) -> SectionItemConstructor:
        raise NotImplementedError()

    def section_item(self,
                     generator_environment: SectionItemGeneratorEnvironment,
                     construction_environment: ConstructionEnvironment) -> doc.SectionItem:
        """Short cut"""
        return self.section_item_constructor(generator_environment).apply(construction_environment)


class SectionHierarchyGenerator:
    """
    Generates a section with sub sections that that appear in the TOC.

    Can be put anywhere in the section hierarchy,
    since it takes an `CustomTargetInfoFactory` as input and uses that to
    generate a `SectionItemGeneratorNode`.
    """

    def generator_node(self, target_factory: TargetInfoFactory) -> SectionItemGeneratorNode:
        raise NotImplementedError()
