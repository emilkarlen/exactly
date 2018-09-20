from typing import List, Optional, Set, Iterable

from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor, \
    SectionConstructor, SectionItemConstructor, ArticleContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNodeEnvironment, \
    SectionItemNode
from exactly_lib.util.textformat.section_target_hierarchy.section_nodes import \
    SectionItemNodeWithSubSections, LeafSectionItemNodeWithRoot, LeafArticleNode
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo, \
    TargetInfoNode, TargetInfoFactoryWithFixedRoot
from exactly_lib.util.textformat.structure import document as doc, core
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.structures import StrOrStringText


def with_fixed_root_target(fixed_root_target: core.CrossReferenceTarget,
                           hierarchy_to_fix_root_target_for: SectionHierarchyGenerator) -> SectionHierarchyGenerator:
    return _HierarchyWithFixedRootTarget(fixed_root_target,
                                         hierarchy_to_fix_root_target_for)


def with_hidden_from_toc(hierarchy_to_hide: SectionHierarchyGenerator) -> SectionHierarchyGenerator:
    return _HierarchyNotInToc(hierarchy_to_hide)


def leaf(header: str,
         contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header), contents_constructor)


def leaf_article(header: StringText,
                 contents_constructor: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None,
                 ) -> SectionHierarchyGenerator:
    """An article without sub sections that appear in the TOC/target hierarchy"""
    return _ArticleLeafGenerator(header,
                                 contents_constructor,
                                 tags=tags)


def leaf_with_constant_target(header: str,
                              constant_target: core.CrossReferenceTarget,
                              contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header),
                                 contents_constructor,
                                 constant_target)


def leaf_article_with_constant_target(header: StringText,
                                      constant_target: core.CrossReferenceTarget,
                                      contents_constructor: ArticleContentsConstructor,
                                      tags: Optional[Set[str]] = None,
                                      ) -> SectionHierarchyGenerator:
    """An article without sub sections that appear in the TOC/target hierarchy"""
    return _ArticleLeafGenerator(header,
                                 contents_constructor,
                                 constant_target,
                                 tags)


def leaf_not_in_toc(section: SectionItemConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that does not appear in the TOC/target hierarchy"""
    return _SectionItemNotInTocLeafGenerator(section)


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


def child(local_target_name: str,
          generator: SectionHierarchyGenerator) -> SectionHierarchyGenerator:
    return _ChildSectionHierarchyGenerator(local_target_name, generator)


def hierarchy(header: StrOrStringText,
              initial_paragraphs: ParagraphItemsConstructor = paragraphs.empty(),
              children: Iterable[SectionHierarchyGenerator] = (),
              ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return _Hierarchy(docs.str_text(header),
                      initial_paragraphs,
                      list(children))


def hierarchy__str(header: str,
                   initial_paragraphs: ParagraphItemsConstructor = paragraphs.empty(),
                   children: Iterable[SectionHierarchyGenerator] = (),
                   ) -> SectionHierarchyGenerator:
    return hierarchy(docs.string_text(header),
                     initial_paragraphs,
                     children)
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return _Hierarchy(header,
                      initial_paragraphs,
                      list(children))


def child_hierarchy(local_target_name: str,
                    header: StrOrStringText,
                    initial_paragraphs: ParagraphItemsConstructor,
                    children: List[SectionHierarchyGenerator],
                    ) -> SectionHierarchyGenerator:
    """
    Short cut to child(hierarchy(...))
    """
    return child(local_target_name,
                 hierarchy(header,
                           initial_paragraphs,
                           children))


def child_leaf(local_target_name: str,
               header: str,
               contents_constructor: SectionContentsConstructor,
               ) -> SectionHierarchyGenerator:
    """
    Short cut to child(leaf(...))
    """
    return child(local_target_name,
                 leaf(header, contents_constructor))


class _ChildSectionHierarchyGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 local_target_name: str,
                 generator: SectionHierarchyGenerator
                 ):
        self._local_target_name = local_target_name
        self._generator = generator

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return self._generator.generate(target_factory.sub_factory(self._local_target_name))


class _SectionHierarchyGeneratorBase(SectionHierarchyGenerator):
    def __init__(self,
                 header: StringText,
                 constant_target: Optional[core.CrossReferenceTarget] = None,
                 ):
        self._header = header
        self._constant_target = constant_target

    def _root_target_info(self, target_factory: TargetInfoFactory) -> TargetInfo:
        if self._constant_target is not None:
            return TargetInfo(self._header,
                              self._constant_target)
        return target_factory.root(self._header)


class _SectionLeafGenerator(_SectionHierarchyGeneratorBase):
    """
    A section without sub sections.
    """

    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor,
                 constant_target: Optional[core.CrossReferenceTarget] = None):
        super().__init__(header, constant_target)
        self._contents_renderer = contents_renderer

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNode(self._root_target_info(target_factory),
                                self._contents_renderer)


class _ArticleLeafGenerator(_SectionHierarchyGeneratorBase):
    """
    An article without sub sections.
    """

    def __init__(self,
                 header: StringText,
                 contents_renderer: ArticleContentsConstructor,
                 constant_target: Optional[core.CrossReferenceTarget] = None,
                 tags: Optional[Set[str]] = None
                 ):
        super().__init__(header, constant_target)
        self._tags = tags
        self._contents_renderer = contents_renderer

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return LeafArticleNode(self._root_target_info(target_factory),
                               self._contents_renderer,
                               self._tags)


class _Hierarchy(_SectionHierarchyGeneratorBase):
    """
    A section with sub sections.
    """

    def __init__(self,
                 header: StringText,
                 initial_paragraphs: ParagraphItemsConstructor,
                 sub_section: List[SectionHierarchyGenerator],
                 constant_target: Optional[core.CrossReferenceTarget] = None,
                 ):
        super().__init__(header, constant_target)
        self._initial_paragraphs = initial_paragraphs
        self._sub_section = sub_section

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        sub_sections = [sub_section.generate(target_factory)
                        for sub_section
                        in self._sub_section
                        ]
        return SectionItemNodeWithSubSections(self._root_target_info(target_factory),
                                              self._initial_paragraphs,
                                              sub_sections)


class _SectionItemNotInTocLeafGenerator(SectionHierarchyGenerator):
    """
    A section item that does not appear in the TOC.
    """

    def __init__(self, section: SectionItemConstructor):
        self._section = section

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNodeNotInToc(self._section)


class _HierarchyWithFixedRootTarget(SectionHierarchyGenerator):
    def __init__(self,
                 fixed_root_target: core.CrossReferenceTarget,
                 hierarchy_to_fix_root_target_for: SectionHierarchyGenerator,
                 ):
        self._fixed_root_target = fixed_root_target
        self._hierarchy_to_fix_root_target_for = hierarchy_to_fix_root_target_for

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return self._hierarchy_to_fix_root_target_for.generate(
            TargetInfoFactoryWithFixedRoot(self._fixed_root_target,
                                           target_factory))


class _HierarchyNotInToc(SectionHierarchyGenerator):
    """
    A section item that does not appear in the TOC.
    """

    def __init__(self, hidden: SectionHierarchyGenerator):
        self._hidden = hidden

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _NodeWithNoTargetInfoNode(self._hidden.generate(target_factory))


class _LeafSectionNode(LeafSectionItemNodeWithRoot):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: SectionContentsConstructor,
                 ):
        super().__init__(node_target_info)
        self._contents_renderer = contents_renderer

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


class _NodeWithNoTargetInfoNode(SectionItemNode):
    """
    A section that have no target info
    """

    def __init__(self, node: SectionItemNode):
        self._section = node

    def target_info_node(self) -> Optional[TargetInfoNode]:
        return None

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionItemConstructor:
        return self._section.section_item_constructor(node_environment)
