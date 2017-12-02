from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.help_texts.cross_reference_id import CustomTargetInfoFactory, TargetInfoNode, TargetInfo
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionConstructor, \
    SectionContentsConstructor, \
    ConstructionEnvironment, ArticleContentsConstructor, ArticleConstructor, SectionItemConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.document import ArticleContents
from exactly_lib.util.textformat.utils import section_item_contents_as_section_contents


class HierarchyRenderingEnvironment:
    def __init__(self, toc_section_item_tags: set):
        self._toc_section_item_tags = toc_section_item_tags

    @property
    def toc_section_item_tags(self) -> set:
        return self._toc_section_item_tags


class SectionItemRendererNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy (for rendering a TOC),
    and one method for getting the corresponding contents.
    """

    def target_info_node(self, ) -> TargetInfoNode:
        raise NotImplementedError()

    def section_item_renderer(self, hierarchy_environment: HierarchyRenderingEnvironment) -> SectionItemConstructor:
        raise NotImplementedError()

    def section_item(self,
                     hierarchy_environment: HierarchyRenderingEnvironment,
                     environment: ConstructionEnvironment) -> doc.SectionItem:
        return self.section_item_renderer(hierarchy_environment).apply(environment)


class SectionItemRendererNodeWithRoot(SectionItemRendererNode):
    """
    A node with a root `TargetInfo` that is a custom target.
    """

    def __init__(self, root_target_info: TargetInfo):
        self._root_target_info = root_target_info

    def target_info_node(self) -> TargetInfoNode:
        raise NotImplementedError()


class SectionHierarchyGenerator:
    """
    A section that can be put anywhere in the section hierarchy, since
    it takes an `CustomTargetInfoFactory` as input and uses that to
    generate a `SectionRendererNode`.
    """

    def renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemRendererNode:
        raise NotImplementedError()


def leaf(header: str,
         contents_renderer: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header), contents_renderer)


def parent(header: str,
           initial_paragraphs: list,
           local_target_name__sub_section__list: list,
           ) -> SectionHierarchyGenerator:
    """
    A section with ub sections that appear in the TOC/target hierarchy.
    :param local_target_name__sub_section__list: [(str, SectionHierarchyGenerator)]
    :param initial_paragraphs: [ParagraphItem]
    """
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     local_target_name__sub_section__list)


class LeafArticleRendererNode(SectionItemRendererNodeWithRoot):
    """
    An article without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: ArticleContentsConstructor,
                 tags: set = None,
                 ):
        super().__init__(node_target_info)
        self._tags = frozenset() if tags is None else tags
        self._contents_renderer = contents_renderer

    def target_info_node(self) -> TargetInfoNode:
        return cross_ref.target_info_leaf(self._root_target_info)

    def section_item_renderer(self, hierarchy_environment: HierarchyRenderingEnvironment) -> ArticleConstructor:
        super_self = self
        tags = self._tags.union(hierarchy_environment.toc_section_item_tags)

        class RetVal(ArticleConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Article:
                article_contents = super_self._contents_renderer.apply(environment)
                return doc.Article(super_self._root_target_info.presentation_text,
                                   ArticleContents(article_contents.abstract_paragraphs,
                                                   article_contents.section_contents),
                                   target=super_self._root_target_info.target,
                                   tags=tags)

        return RetVal()


HIERARCHY_SECTION_TAG = 'toc'

_HIERARCHY_SECTION_TAGS = {HIERARCHY_SECTION_TAG}


class SectionItemRendererNodeWithSubSections(SectionItemRendererNodeWithRoot):
    """
    A section with sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 root_target_info: TargetInfo,
                 initial_paragraphs: list,
                 sub_sections: list,
                 ):
        """
        :param root_target_info: Root section
        :param initial_paragraphs: [ParagraphItem]
        :param sub_sections: [SectionRendererNode]
        """
        super().__init__(root_target_info)
        self._sub_section_nodes = sub_sections
        self._initial_paragraphs = initial_paragraphs

    def target_info_node(self) -> TargetInfoNode:
        return TargetInfoNode(self._root_target_info,
                              [ss.target_info_node()
                               for ss in self._sub_section_nodes])

    def section_item_renderer(self, hierarchy_environment: HierarchyRenderingEnvironment) -> SectionItemConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                sub_sections = [ss.section_item_renderer(hierarchy_environment).apply(environment)
                                for ss in super_self._sub_section_nodes]
                return doc.Section(super_self._root_target_info.presentation_text,
                                   doc.SectionContents(super_self._initial_paragraphs,
                                                       sub_sections),
                                   target=super_self._root_target_info.target,
                                   tags=hierarchy_environment.toc_section_item_tags)

        return RetVal()


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

    def renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemRendererNode:
        return _LeafSectionRendererNode(target_factory.root(self._header),
                                        self._contents_renderer)


class _SectionHierarchyGeneratorWithSubSections(SectionHierarchyGenerator):
    """
    A section with sub sections.
    """

    def __init__(self,
                 header: StringText,
                 initial_paragraphs: list,
                 local_target_name__sub_section__list: list,
                 ):
        """
        :param header:
        :param local_target_name__sub_section__list: [(str, SectionGenerator)]
        :param initial_paragraphs: [ParagraphItem]
        """
        self._header = header
        self._local_target_name__sub_section__list = local_target_name__sub_section__list
        self._initial_paragraphs = initial_paragraphs

    def renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemRendererNode:
        sub_sections = [section_generator.renderer_node(target_factory.sub_factory(local_target_name))
                        for (local_target_name, section_generator)
                        in self._local_target_name__sub_section__list]
        return SectionItemRendererNodeWithSubSections(target_factory.root(self._header),
                                                      self._initial_paragraphs,
                                                      sub_sections)


class _LeafSectionRendererNode(SectionItemRendererNodeWithRoot):
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
        return cross_ref.target_info_leaf(self._root_target_info)

    def section_item_renderer(self, hierarchy_environment: HierarchyRenderingEnvironment) -> SectionConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                return doc.Section(super_self._root_target_info.presentation_text,
                                   super_self._contents_renderer.apply(environment),
                                   target=super_self._root_target_info.target,
                                   tags=hierarchy_environment.toc_section_item_tags)

        return RetVal()


class SectionContentsConstructorFromHierarchyGenerator(SectionContentsConstructor):
    """
    Transforms a `SectionGenerator` to a `SectionContentsRenderer`,
    for usages where section header and target hierarchy is irrelevant.
    """

    def __init__(self, generator: SectionHierarchyGenerator):
        self.generator = generator

    def apply(self, environment: ConstructionEnvironment) -> SectionContents:
        target_factory = CustomTargetInfoFactory('ignored')
        section_item = self.generator.renderer_node(target_factory).section_item(HierarchyRenderingEnvironment(set()),
                                                                                 environment)
        return section_item_contents_as_section_contents(section_item)
