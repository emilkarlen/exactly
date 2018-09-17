from typing import Sequence, Optional, Set

from exactly_lib.util.textformat.construction.section_contents.constructor import \
    SectionItemConstructor, \
    ConstructionEnvironment, ArticleContentsConstructor, ArticleConstructor, SectionConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.structure import SectionItemGeneratorEnvironment, \
    SectionItemGeneratorNode
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode, TargetInfo
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import ArticleContents


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
    An article who's sub sections do not appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None,
                 ):
        super().__init__(node_target_info)
        self._tags = frozenset() if tags is None else tags
        self._contents_renderer = contents_renderer

    def target_info_node(self) -> TargetInfoNode:
        return targets.target_info_leaf(self._root_target_info)

    def section_item_constructor(self, generator_environment: SectionItemGeneratorEnvironment) -> ArticleConstructor:
        super_self = self
        tags = self._tags.union(generator_environment.toc_section_item_tags)

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
    A section who's sub sections do not appear in the target-hierarchy.
    """

    def __init__(self,
                 root_target_info: TargetInfo,
                 initial_paragraphs: Sequence[ParagraphItem],
                 sub_sections: Sequence[SectionItemGeneratorNode],
                 ):
        super().__init__(root_target_info)
        self._initial_paragraphs = initial_paragraphs
        self._sub_sections = sub_sections

    def target_info_node(self) -> TargetInfoNode:
        return TargetInfoNode(self._root_target_info,
                              [ss.target_info_node()
                               for ss in self._sub_sections])

    def section_item_constructor(self,
                                 generator_environment: SectionItemGeneratorEnvironment) -> SectionItemConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                sub_sections = [ss.section_item_constructor(generator_environment).apply(environment)
                                for ss in super_self._sub_sections]
                return doc.Section(super_self._root_target_info.presentation_text,
                                   doc.SectionContents(list(super_self._initial_paragraphs),
                                                       sub_sections),
                                   target=super_self._root_target_info.target,
                                   tags=generator_environment.toc_section_item_tags)

        return RetVal()
