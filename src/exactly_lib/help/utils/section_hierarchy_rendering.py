from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, TargetInfoNode
from exactly_lib.help.utils.section_contents_renderer import SectionRenderer, SectionContentsRenderer, \
    RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


class SectionRendererNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy (for rendering a TOC),
    and one method for getting the corresponding contents.
    """

    def __init__(self,
                 header: str,
                 target_factory: CustomTargetInfoFactory):
        self._target_factory = target_factory
        self._root_target_info = target_factory.root(header)

    def target_info_node(self, ) -> TargetInfoNode:
        raise NotImplementedError()

    def section_renderer(self) -> SectionRenderer:
        raise NotImplementedError()


class SectionGenerator:
    """
    A section that can be put anywhere in the section hierarchy, since
    it takes an `CustomTargetInfoFactory` as input and uses that to
    generate a `SectionRendererNode`.
    """

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        raise NotImplementedError()


class LeafSectionRendererNode(SectionRendererNode):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 header: str,
                 contents_renderer: SectionContentsRenderer,
                 target_factory: CustomTargetInfoFactory,
                 ):
        super().__init__(header, target_factory)
        self._contents_renderer = contents_renderer

    def target_info_node(self) -> TargetInfoNode:
        return cross_ref.target_info_leaf(self._root_target_info)

    def section_renderer(self) -> SectionRenderer:
        super_self = self

        class RetVal(SectionRenderer):
            def apply(self, environment: RenderingEnvironment) -> doc.Section:
                return doc.Section(super_self._root_target_info.anchor_text(),
                                   super_self._contents_renderer.apply(environment))

        return RetVal()


class SubSection:
    def __init__(self,
                 target_component: str,
                 sub_section_node: SectionRendererNode):
        self.target_component = target_component
        self.sub_section_node = sub_section_node


class SectionRendererNodeWithSubSections(SectionRendererNode):
    """
    A section with sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 header: str,
                 initial_paragraphs: list,
                 sub_sections: list,
                 target_factory: CustomTargetInfoFactory,
                 ):
        """
        :param header:
        :param sub_sections: [SectionRendererNode]
        :param initial_paragraphs: [ParagraphItem]
        :param target_factory:
        """
        super().__init__(header, target_factory)
        self._sub_section_nodes = sub_sections
        self._initial_paragraphs = initial_paragraphs

    def target_info_node(self) -> TargetInfoNode:
        return TargetInfoNode(self._root_target_info,
                              [ss.target_info_node()
                               for ss in self._sub_section_nodes])

    def section_renderer(self) -> SectionRenderer:
        super_self = self

        class RetVal(SectionRenderer):
            def apply(self, environment: RenderingEnvironment) -> doc.Section:
                sub_sections = [ss.section_renderer().apply(environment)
                                for ss in super_self._sub_section_nodes]
                return doc.Section(super_self._root_target_info.anchor_text(),
                                   doc.SectionContents(super_self._initial_paragraphs,
                                                       sub_sections))

        return RetVal()


class SectionGeneratorLeaf(SectionGenerator):
    """
    A section without sub sections.
    """

    def __init__(self,
                 header: str,
                 contents_renderer: SectionContentsRenderer,
                 ):
        self._header = header
        self._contents_renderer = contents_renderer

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        return LeafSectionRendererNode(self._header,
                                       self._contents_renderer,
                                       target_factory)


class SectionGeneratorWithSubSections(SectionGenerator):
    """
    A section with sub sections.
    """

    def __init__(self,
                 header: str,
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

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        def sub_factory(local_target_name: str) -> CustomTargetInfoFactory:
            return cross_ref.sub_component_factory(local_target_name, target_factory)

        sub_sections = [section_generator.section_renderer_node(sub_factory(local_target_name))
                        for (local_target_name, section_generator)
                        in self._local_target_name__sub_section__list]
        return SectionRendererNodeWithSubSections(self._header,
                                                  self._initial_paragraphs,
                                                  sub_sections,
                                                  target_factory)
