from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.cli.cli_environment import program_info
from shellcheck_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from shellcheck_lib.help import cross_reference_id as cross_ref
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.cross_reference_id import CustomTargetInfoFactory
from shellcheck_lib.help.program_modes.test_case.contents.main import overview as overview_content
from shellcheck_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.util.std import StdOutputFiles
from shellcheck_lib.util.textformat.formatting.html import document as doc_rendering
from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.formatting.html.utils import ElementPopulator
from shellcheck_lib.util.textformat.structure import core as doc
from shellcheck_lib.util.textformat.structure import lists as doc_list
from shellcheck_lib.util.textformat.structure import structures as docs
from shellcheck_lib.util.textformat.structure.document import SectionContents

ELEMENT_STYLES = """\
pre {
background: lightgray;
}
"""

TITLE_STYLE = """\
font-size: 250%;
font-weight: bold;
"""

PAGE_TITLE = '%s Reference Manual' % program_info.PROGRAM_NAME


class HtmlGenerationRequestHandler(RequestHandler):
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help

    def handle(self,
               output: StdOutputFiles):
        setup = self._setup()
        section_renderer = _section_renderer()
        renderer = doc_rendering.DocumentRenderer(section_renderer)
        contents = self._contents()
        renderer.apply(output.out, setup, contents)

    def _setup(self) -> doc_rendering.DocumentSetup:
        head_populator = StylePopulator(ELEMENT_STYLES)
        header_populator = TitleAndVersionPopulator()
        setup = doc_rendering.DocumentSetup(PAGE_TITLE,
                                            head_populator=head_populator,
                                            header_populator=header_populator)
        return setup

    def _contents(self) -> SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, main_contents = self._main_contents(
            cross_ref.sub_component_factory('tc-overview',
                                            root_targets_factory))
        toc_paragraph = toc_list(target_info_hierarchy)
        main_contents.initial_paragraphs.insert(0, toc_paragraph)
        return main_contents

    def _main_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, SectionContents):
        generator = overview_content.OverviewRenderer(self.application_help.test_case_help,
                                                      targets_factory)
        cross_reference_text_constructor = CrossReferenceTextConstructor()
        environment = RenderingEnvironment(cross_reference_text_constructor)
        section_contents = generator.apply(environment)
        return generator.target_info_hierarchy(), section_contents


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = _TargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)


class _TargetRenderer(text.TargetRenderer, cross_ref.CrossReferenceIdVisitor):
    def apply(self, target: doc.CrossReferenceTarget) -> str:
        return self.visit(target)

    def visit_concept(self, x: cross_ref.ConceptCrossReferenceId):
        return x.concept_name

    def visit_custom(self, x: cross_ref.CustomCrossReferenceId):
        return x.target_name


class StylePopulator(ElementPopulator):
    def __init__(self, style: str):
        self.style = style

    def apply(self, parent: Element):
        SubElement(parent, 'style').text = self.style


class TitleAndVersionPopulator(ElementPopulator):
    def apply(self, parent: Element):
        div = SubElement(parent, 'div')
        div.text = PAGE_TITLE
        div.set('style', TITLE_STYLE)
        version = SubElement(parent, 'p')
        version.text = program_info.PROGRAM_NAME + ' version ' + program_info.VERSION
        SubElement(parent, 'hr')


def toc_list(target_info_hierarchy: list) -> doc.ParagraphItem:
    items = []
    for x in target_info_hierarchy:
        if isinstance(x, cross_ref.TargetInfo):
            item = doc_list.HeaderContentListItem(docs.cross_reference(x.presentation_str,
                                                                       x.target),
                                                  [])
            items.append(item)
        elif isinstance(x, list):
            item = toc_list(x)
            items.append(item)
        else:
            msg = 'An element in a TargetInfo hierarchy must be either a %s or a %s. Found: %s' % (
                str(cross_ref.TargetInfo),
                str(list),
                str(x))
            raise TypeError(msg)
    return doc_list.HeaderContentList(items,
                                      doc_list.Format(doc_list.ListType.ORDERED_LIST))
