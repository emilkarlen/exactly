from typing import Sequence, Optional, Set

from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import \
    SectionItemConstructor, \
    ArticleContentsConstructor, ArticleConstructor, SectionConstructor
from exactly_lib.util.textformat.section_target_hierarchy import targets
from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNodeEnvironment, \
    SectionItemNode
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoNode, TargetInfo
from exactly_lib.util.textformat.structure import document as doc


class SectionItemNodeWithRoot(SectionItemNode):
    """
    A node with a root `TargetInfo` that is a custom target.
    """

    def __init__(self, root_target_info: TargetInfo):
        self._root_target_info = root_target_info

    def target_info_node(self) -> Optional[TargetInfoNode]:
        raise NotImplementedError('abstract method')


class LeafSectionItemNodeWithRoot(SectionItemNodeWithRoot):
    """
    A node with a root `TargetInfo` that is a custom target.
    """

    def __init__(self, node_target_info: TargetInfo):
        super().__init__(node_target_info)

    def target_info_node(self) -> Optional[TargetInfoNode]:
        return targets.target_info_leaf(self._root_target_info)


class LeafArticleNode(LeafSectionItemNodeWithRoot):
    """
    An article who's sub sections do not appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None,
                 ):
        super().__init__(node_target_info)
        self._tags = tags
        self._contents_renderer = contents_renderer

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> ArticleConstructor:
        tags = self._tags.union(node_environment.toc_section_item_tags)

        return sections.article(self._root_target_info,
                                self._contents_renderer,
                                tags,
                                )


class SectionItemNodeWithSubSections(SectionItemNodeWithRoot):
    """
    A section who's sub sections do not appear in the target-hierarchy.
    """

    def __init__(self,
                 root_target_info: TargetInfo,
                 initial_paragraphs: ParagraphItemsConstructor,
                 sub_sections: Sequence[SectionItemNode],
                 ):
        super().__init__(root_target_info)
        self._initial_paragraphs = initial_paragraphs
        self._sub_sections = sub_sections

    def target_info_node(self) -> Optional[TargetInfoNode]:
        sub_nodes = [ss.target_info_node()
                     for ss in self._sub_sections]
        return TargetInfoNode(self._root_target_info,
                              [x for x in sub_nodes if x is not None])

    def section_item_constructor(self, node_environment: SectionItemNodeEnvironment) -> SectionItemConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                sub_sections = [ss.section_item_constructor(node_environment).apply(environment)
                                for ss in super_self._sub_sections]
                return doc.Section(super_self._root_target_info.presentation_text,
                                   doc.SectionContents(super_self._initial_paragraphs.apply(environment),
                                                       sub_sections),
                                   target=super_self._root_target_info.target,
                                   tags=node_environment.toc_section_item_tags)

        return RetVal()
