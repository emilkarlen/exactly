from exactly_lib.util.textformat.construction.section_contents_constructor import SectionItemConstructor, \
    ConstructionEnvironment, ArticleContentsConstructor, ArticleConstructor, SectionConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode, TargetInfo, \
    CustomTargetInfoFactory
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.document import ArticleContents


class HierarchyGeneratorEnvironment:
    def __init__(self, toc_section_item_tags: set):
        self._toc_section_item_tags = toc_section_item_tags

    @property
    def toc_section_item_tags(self) -> set:
        return self._toc_section_item_tags


class SectionItemGeneratorNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy (for rendering a TOC),
    and one method for getting the corresponding contents.
    """

    def target_info_node(self, ) -> TargetInfoNode:
        raise NotImplementedError()

    def section_item_constructor(self, hierarchy_environment: HierarchyGeneratorEnvironment
                                 ) -> SectionItemConstructor:
        raise NotImplementedError()

    def section_item(self,
                     hierarchy_environment: HierarchyGeneratorEnvironment,
                     environment: ConstructionEnvironment) -> doc.SectionItem:
        return self.section_item_constructor(hierarchy_environment).apply(environment)


class SectionHierarchyGenerator:
    """
    A section that can be put anywhere in the section hierarchy, since
    it takes an `CustomTargetInfoFactory` as input and uses that to
    generate a `SectionItemGeneratorNode`.
    """

    def generator_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemGeneratorNode:
        raise NotImplementedError()


class SectionItemGeneratorNodeWithRoot(SectionItemGeneratorNode):
    """
    A node with a root `TargetInfo` that is a custom target.
    """

    def __init__(self, root_target_info: TargetInfo):
        self._root_target_info = root_target_info

    def target_info_node(self) -> TargetInfoNode:
        raise NotImplementedError('abstract method')


class LeafArticleGeneratorNode(SectionItemGeneratorNodeWithRoot):
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
        return targets.target_info_leaf(self._root_target_info)

    def section_item_constructor(self, hierarchy_environment: HierarchyGeneratorEnvironment) -> ArticleConstructor:
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


class SectionItemGeneratorNodeWithSubSections(SectionItemGeneratorNodeWithRoot):
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
        :param sub_sections: [SectionItemGeneratorNode]
        """
        super().__init__(root_target_info)
        self._sub_section_nodes = sub_sections
        self._initial_paragraphs = initial_paragraphs

    def target_info_node(self) -> TargetInfoNode:
        return TargetInfoNode(self._root_target_info,
                              [ss.target_info_node()
                               for ss in self._sub_section_nodes])

    def section_item_constructor(self, hierarchy_environment: HierarchyGeneratorEnvironment
                                 ) -> SectionItemConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                sub_sections = [ss.section_item_constructor(hierarchy_environment).apply(environment)
                                for ss in super_self._sub_section_nodes]
                return doc.Section(super_self._root_target_info.presentation_text,
                                   doc.SectionContents(super_self._initial_paragraphs,
                                                       sub_sections),
                                   target=super_self._root_target_info.target,
                                   tags=hierarchy_environment.toc_section_item_tags)

        return RetVal()
