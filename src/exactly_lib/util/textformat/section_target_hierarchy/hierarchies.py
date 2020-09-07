from typing import Optional, Set, Iterable

from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor, \
    SectionConstructor, ArticleContentsConstructor
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


def leaf(header: StrOrStringText,
         contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(docs.str_text(header), contents_constructor)


def leaf_not_in_toc(header: StrOrStringText,
                    contents_constructor: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafNotInTocGenerator(docs.str_text(header), contents_constructor)


def leaf_article(header: StrOrStringText,
                 contents_constructor: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None,
                 ) -> SectionHierarchyGenerator:
    """An article without sub sections that appear in the TOC/target hierarchy"""
    return _ArticleLeafGenerator(docs.str_text(header),
                                 contents_constructor,
                                 tags=tags)


def child(local_target_name: str,
          generator: SectionHierarchyGenerator) -> SectionHierarchyGenerator:
    return _ChildSectionHierarchyGenerator(local_target_name, generator)


def child_leaf(local_target_name: str,
               header: StrOrStringText,
               contents_constructor: SectionContentsConstructor,
               ) -> SectionHierarchyGenerator:
    """
    Short cut to child(leaf(...))
    """
    return child(local_target_name,
                 leaf(header, contents_constructor))


def hierarchy(header: StrOrStringText,
              initial_paragraphs: ParagraphItemsConstructor = paragraphs.empty(),
              children: Iterable[SectionHierarchyGenerator] = (),
              ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    """
    return _Hierarchy(docs.str_text(header),
                      initial_paragraphs,
                      children)


def child_hierarchy(local_target_name: str,
                    header: StrOrStringText,
                    initial_paragraphs: ParagraphItemsConstructor,
                    children: Iterable[SectionHierarchyGenerator],
                    ) -> SectionHierarchyGenerator:
    """
    Short cut to child(hierarchy(...))
    """
    return child(local_target_name,
                 hierarchy(header,
                           initial_paragraphs,
                           children))


def with_fixed_root_target(fixed_root_target: core.CrossReferenceTarget,
                           hierarchy_to_fix_root_target_for: SectionHierarchyGenerator) -> SectionHierarchyGenerator:
    return _HierarchyWithFixedRootTarget(fixed_root_target,
                                         hierarchy_to_fix_root_target_for)


class _ChildSectionHierarchyGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 local_target_name: str,
                 generator: SectionHierarchyGenerator
                 ):
        self._local_target_name = local_target_name
        self._generator = generator

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return self._generator.generate(target_factory.sub_factory(self._local_target_name))


class _SectionLeafGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor):
        self._header = header
        self._contents_renderer = contents_renderer

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafSectionNode(target_factory.root(self._header),
                                self._contents_renderer)


class _SectionLeafNotInTocGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor):
        self._header = header
        self._contents_renderer = contents_renderer

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return _LeafNotInTocSectionNode(self._header,
                                        self._contents_renderer)


class _ArticleLeafGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 header: StringText,
                 contents_renderer: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None
                 ):
        self._header = header
        self._contents_renderer = contents_renderer
        self._tags = tags

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        return LeafArticleNode(target_factory.root(self._header),
                               self._contents_renderer,
                               self._tags)


class _Hierarchy(SectionHierarchyGenerator):
    def __init__(self,
                 header: StringText,
                 initial_paragraphs: ParagraphItemsConstructor,
                 sub_section: Iterable[SectionHierarchyGenerator],
                 ):
        self._header = header
        self._initial_paragraphs = initial_paragraphs
        self._sub_section = sub_section

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        sub_sections = [sub_section.generate(target_factory)
                        for sub_section
                        in self._sub_section
                        ]
        return SectionItemNodeWithSubSections(target_factory.root(self._header),
                                              self._initial_paragraphs,
                                              sub_sections)


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


class _LeafNotInTocSectionNode(SectionItemNode):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 header: StringText,
                 contents_renderer: SectionContentsConstructor,
                 ):
        self._header = header
        self._contents_renderer = contents_renderer

    def target_info_node(self) -> Optional[TargetInfoNode]:
        return None

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                return doc.Section(super_self._header,
                                   super_self._contents_renderer.apply(environment),
                                   target=None,
                                   tags=None)

        return RetVal()
