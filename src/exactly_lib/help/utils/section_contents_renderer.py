from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc


class RenderingEnvironment(tuple):
    def __new__(cls,
                cross_ref_text_constructor: CrossReferenceTextConstructor,
                render_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   render_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def render_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]


class SectionContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()


class SectionRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.Section:
        raise NotImplementedError()


class SectionRendererFromHeaderAndContents(SectionRenderer):
    def __init__(self,
                 header: doc.core.Text,
                 section_contents_renderer: SectionContentsRenderer):
        self.header = header
        self.section_contents_renderer = section_contents_renderer

    def apply(self, environment: RenderingEnvironment) -> doc.Section:
        return doc.Section(self.header,
                           self.section_contents_renderer.apply(environment))


class SectionNode:
    def target_info_node(self) -> cross_ref.TargetInfoNode:
        raise NotImplementedError()

    def section_renderer(self) -> SectionRenderer:
        raise NotImplementedError()


class LeafSectionNode(SectionNode):
    def __init__(self,
                 header: str,
                 target_factory: cross_ref.CustomTargetInfoFactory,
                 contents_renderer: SectionContentsRenderer):
        self.target_info = target_factory.root(header)
        self.contents_renderer = contents_renderer

    def target_info_node(self) -> cross_ref.TargetInfoNode:
        return cross_ref.target_info_leaf(self.target_info)

    def section_renderer(self) -> SectionRenderer:
        return SectionRendererFromHeaderAndContents(self.target_info.anchor_text(),
                                                    self.contents_renderer)
