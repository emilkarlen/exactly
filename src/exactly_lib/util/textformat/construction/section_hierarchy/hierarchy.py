from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    SectionConstructor, ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionHierarchyGenerator, \
    SectionItemGeneratorNode, SectionItemGeneratorNodeWithRoot, \
    HierarchyGeneratorEnvironment, SectionItemGeneratorNodeWithSubSections
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CustomTargetInfoFactory, TargetInfo, \
    TargetInfoNode
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import StringText


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
           initial_paragraphs: list,
           local_target_name__sub_section__list: list,
           ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    :param local_target_name__sub_section__list: [(str, SectionHierarchyGenerator)] or list of `Node`
    :param initial_paragraphs: [ParagraphItem]
    """
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     local_target_name__sub_section__list)


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

    def generator_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemGeneratorNode:
        return _LeafSectionGeneratorNode(target_factory.root(self._header),
                                         self._contents_renderer)


class _LeafSectionGeneratorNode(SectionItemGeneratorNodeWithRoot):
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

    def section_item_constructor(self, hierarchy_environment: HierarchyGeneratorEnvironment) -> SectionConstructor:
        super_self = self

        class RetVal(SectionConstructor):
            def apply(self, environment: ConstructionEnvironment) -> doc.Section:
                return doc.Section(super_self._root_target_info.presentation_text,
                                   super_self._contents_renderer.apply(environment),
                                   target=super_self._root_target_info.target,
                                   tags=hierarchy_environment.toc_section_item_tags)

        return RetVal()


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
        :param local_target_name__sub_section__list: [(str, SectionItemGeneratorNode)]
        :param initial_paragraphs: [ParagraphItem]
        """
        self._header = header
        self._local_target_name__sub_section__list = local_target_name__sub_section__list
        self._initial_paragraphs = initial_paragraphs

    def generator_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemGeneratorNode:
        sub_sections = [section_generator.generator_node(target_factory.sub_factory(local_target_name))
                        for (local_target_name, section_generator)
                        in self._local_target_name__sub_section__list]
        return SectionItemGeneratorNodeWithSubSections(target_factory.root(self._header),
                                                       self._initial_paragraphs,
                                                       sub_sections)
