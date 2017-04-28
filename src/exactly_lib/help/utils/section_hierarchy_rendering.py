from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, TargetInfoNode, TargetInfo
from exactly_lib.help.utils.section_contents_renderer import SectionRenderer, SectionContentsRenderer, \
    RenderingEnvironment
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.textformat.structure import document as doc


class SectionRendererNode:
    """
    A node in the tree of sections with corresponding targets.

    Supplies one method for getting the target-hierarchy (for rendering a TOC),
    and one method for getting the corresponding contents.
    """

    def target_info_node(self, ) -> TargetInfoNode:
        raise NotImplementedError()

    def section_renderer(self) -> SectionRenderer:
        raise NotImplementedError()

    def section(self, environment: RenderingEnvironment) -> doc.Section:
        return self.section_renderer().apply(environment)


class SectionRendererNodeWithRoot(SectionRendererNode):
    """
    A node with a root `TargetInfo` that is a custom target.
    """

    def __init__(self, root_target_info: TargetInfo):
        self._root_target_info = root_target_info

    def target_info_node(self, ) -> TargetInfoNode:
        raise NotImplementedError()

    def section_renderer(self) -> SectionRenderer:
        raise NotImplementedError()

    def section(self, environment: RenderingEnvironment) -> doc.Section:
        return self.section_renderer().apply(environment)


class SectionGenerator:
    """
    A section that can be put anywhere in the section hierarchy, since
    it takes an `CustomTargetInfoFactory` as input and uses that to
    generate a `SectionRendererNode`.
    """

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        raise NotImplementedError()


def leaf(header: str,
         contents_renderer: SectionContentsRenderer) -> SectionGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionGeneratorLeaf(header, contents_renderer)


def parent(header: str,
           initial_paragraphs: list,
           local_target_name__sub_section__list: list,
           ) -> SectionGenerator:
    """
    A section with ub sections that appear in the TOC/target hierarchy.
    :param local_target_name__sub_section__list: [(str, SectionGenerator)]
    :param initial_paragraphs: [ParagraphItem]
    """
    return _SectionGeneratorWithSubSections(header, initial_paragraphs, local_target_name__sub_section__list)


class LeafSectionRendererNode(SectionRendererNodeWithRoot):
    """
    A section without sub sections that appear in the target-hierarchy.
    """

    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: SectionContentsRenderer,
                 ):
        super().__init__(node_target_info)
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


class SectionRendererNodeWithSubSections(SectionRendererNodeWithRoot):
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


class _SectionGeneratorLeaf(SectionGenerator):
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
        return LeafSectionRendererNode(target_factory.root(self._header),
                                       self._contents_renderer)


class _SectionGeneratorWithSubSections(SectionGenerator):
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
        return SectionRendererNodeWithSubSections(target_factory.root(self._header),
                                                  self._initial_paragraphs,
                                                  sub_sections)


class SectionFromGeneratorAsSectionContentsRenderer(SectionContentsRenderer):
    """
    Transforms a `SectionGenerator` to a `SectionContentsRenderer`,
    for usages where section header and target hierarchy is irrelevant.
    """

    def __init__(self, generator: SectionGenerator):
        self.generator = generator

    def apply(self, environment: RenderingEnvironment) -> SectionContents:
        target_factory = CustomTargetInfoFactory('arbitrary')
        return self.generator.section_renderer_node(target_factory).section(environment).contents
