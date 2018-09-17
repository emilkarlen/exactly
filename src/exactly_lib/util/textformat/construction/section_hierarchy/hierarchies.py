from typing import List

from exactly_lib.util.textformat.construction.section_contents.constructor import \
    SectionContentsConstructor, \
    SectionConstructor, ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.section_node import SectionItemNodeEnvironment, \
    SectionItemNode
from exactly_lib.util.textformat.construction.section_hierarchy.section_nodes import \
    SectionItemNodeWithRoot, \
    SectionItemNodeWithSubSections
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoFactory, TargetInfo, \
    TargetInfoNode
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import StringText, ParagraphItem


def leaf(header: str,
         contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header), contents_constructor)


class Node(tuple):
    """A SectionHierarchyGenerator with a local target name."""

    def __new__(cls,
                local_target_name: str,
                generator: SectionHierarchyGenerator):
        return tuple.__new__(cls, (local_target_name, generator))

    @property
    def local_target_name(self) -> str:
        return self[0]

    @property
    def generator(self) -> SectionHierarchyGenerator:
        return self[1]


def parent(header: str,
           initial_paragraphs: List[ParagraphItem],
           nodes: List[Node],
           ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     nodes)


class _SectionLeafGenerator(SectionHierarchyGenerator):
    """
    A section without sub sections.
    """

    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor,
                 ):
        self._header = header
        self._contents_renderer = contents_renderer

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNode(target_factory.root(self._header),
                                self._contents_renderer)


class _LeafSectionNode(SectionItemNodeWithRoot):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: SectionContentsConstructor,
                 ):
        super().__init__(node_target_info)
        self._contents_renderer = contents_renderer

    def target_info_node(self) -> TargetInfoNode:
        return targets.target_info_leaf(self._root_target_info)

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                return doc.Section(super_self._root_target_info.presentation_text,
                                   super_self._contents_renderer.apply(environment),
                                   target=super_self._root_target_info.target,
                                   tags=node_environment.toc_section_item_tags)

        return RetVal()


class _SectionHierarchyGeneratorWithSubSections(SectionHierarchyGenerator):
    """
    A section with sub sections.
    """

    def __init__(self,
                 header: StringText,
                 initial_paragraphs: List[ParagraphItem],
                 nodes: List[Node],
                 ):
        self._header = header
        self._initial_paragraphs = initial_paragraphs
        self._nodes = nodes

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        sub_sections = [node.generator.generate(target_factory.sub_factory(node.local_target_name))
                        for node
                        in self._nodes
                        ]
        return SectionItemNodeWithSubSections(target_factory.root(self._header),
                                              self._initial_paragraphs,
                                              sub_sections)
