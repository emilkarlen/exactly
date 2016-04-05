from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.cli.cli_environment import program_info
from shellcheck_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.program_modes.test_case.contents.main import overview as overview_content
from shellcheck_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.util.std import StdOutputFiles
from shellcheck_lib.util.textformat.formatting.html import document as doc_rendering
from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.formatting.html.utils import ElementPopulator
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure.document import SectionContents

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
        header_populator = TitleAndVersionPopulator()
        setup = doc_rendering.DocumentSetup(PAGE_TITLE,
                                            header_populator=header_populator)
        return setup

    def _contents(self) -> SectionContents:
        generator = overview_content.OverviewRenderer(self.application_help.test_case_help)
        cross_reference_text_constructor = CrossReferenceTextConstructor()
        environment = RenderingEnvironment(cross_reference_text_constructor)
        return generator.apply(environment)


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = _TargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)


class _TargetRenderer(text.TargetRenderer):
    def apply(self, target: core.CrossReferenceTarget) -> str:
        return 'TODO TargetRenderer'


class TitleAndVersionPopulator(ElementPopulator):
    def apply(self, parent: Element):
        div = SubElement(parent, 'div')
        div.text = PAGE_TITLE
        div.set('style', TITLE_STYLE)
        version = SubElement(parent, 'p')
        version.text = 'Version ' + program_info.VERSION
        SubElement(parent, 'hr')
