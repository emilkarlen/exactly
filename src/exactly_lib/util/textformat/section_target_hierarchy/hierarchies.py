from typing import List, Optional

from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor, \
    SectionConstructor, SectionItemConstructor
from exactly_lib.util.textformat.section_target_hierarchy import targets
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNodeEnvironment, \
    SectionItemNode
from exactly_lib.util.textformat.section_target_hierarchy.section_nodes import \
    SectionItemNodeWithRoot, \
    SectionItemNodeWithSubSections
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo, \
    TargetInfoNode
from exactly_lib.util.textformat.structure import document as doc, core
from exactly_lib.util.textformat.structure.core import StringText, ParagraphItem


def leaf(header: str,
         contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header), contents_constructor)


def leaf_with_constant_target(header: str,
                              constant_target: core.CrossReferenceTarget,
                              contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header),
                                 contents_constructor,
                                 constant_target)


def leaf_not_in_toc(section: SectionItemConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that does not appear in the TOC/target hierarchy"""
    return _SectionNotInTocLeafGenerator(section)


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


def parent_(header: str,
            initial_paragraphs: List[ParagraphItem],
            nodes: List[Node],
            ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return parent(header,
                  paragraphs.constant(initial_paragraphs),
                  nodes)


def parent(header: str,
           initial_paragraphs: ParagraphItemsConstructor,
           nodes: List[Node],
           ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     nodes)


def sections(header: str,
             nodes: List[Node],
             ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return parent(header,
                  paragraphs.empty(),
                  nodes)


def hierarchy_with_constant_target(header: str,
                                   constant_target: core.CrossReferenceTarget,
                                   initial_paragraphs: ParagraphItemsConstructor,
                                   nodes: List[Node],
                                   ) -> SectionHierarchyGenerator:
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     nodes,
                                                     constant_target,
                                                     )


class _SectionLeafGenerator(SectionHierarchyGenerator):
    """
    A section without sub sections.
    """

    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor,
                 constant_target: Optional[core.CrossReferenceTarget] = None,
                 ):
        self._header = header
        self._contents_renderer = contents_renderer
        self._constant_target = constant_target

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNode(self._root_target_info(target_factory),
                                self._contents_renderer)

    def _root_target_info(self, target_factory: TargetInfoFactory) -> TargetInfo:
        if self._constant_target is not None:
            return TargetInfo(self._header,
                              self._constant_target)
        return target_factory.root(self._header)


class _SectionNotInTocLeafGenerator(SectionHierarchyGenerator):
    """
    A section that does not appear in the TOC.
    """

    def __init__(self, section: SectionItemConstructor):
        self._section = section

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNodeNotInToc(self._section)


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

    def target_info_node(self) -> Optional[TargetInfoNode]:
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


class _LeafSectionNodeNotInToc(SectionItemNode):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self, section: SectionItemConstructor):
        self._section = section

    def target_info_node(self) -> Optional[TargetInfoNode]:
        return None

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionItemConstructor:
        return self._section


class _SectionHierarchyGeneratorWithSubSections(SectionHierarchyGenerator):
    """
    A section with sub sections.
    """

    def __init__(self,
                 header: StringText,
                 initial_paragraphs: ParagraphItemsConstructor,
                 nodes: List[Node],
                 constant_target: Optional[core.CrossReferenceTarget] = None,
                 ):
        self._header = header
        self._initial_paragraphs = initial_paragraphs
        self._nodes = nodes
        self._constant_target = constant_target

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        sub_sections = [node.generator.generate(target_factory.sub_factory(node.local_target_name))
                        for node
                        in self._nodes
                        ]
        return SectionItemNodeWithSubSections(self._root_target_info(target_factory),
                                              self._initial_paragraphs,
                                              sub_sections)

    def _root_target_info(self, target_factory: TargetInfoFactory) -> TargetInfo:
        if self._constant_target is not None:
            return TargetInfo(self._header,
                              self._constant_target)
        return target_factory.root(self._header)
