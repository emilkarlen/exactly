from xml.etree.ElementTree import Element, SubElement

from shellcheck_lib.cli.cli_environment import program_info
from shellcheck_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from shellcheck_lib.help import cross_reference_id as cross_ref
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.cross_reference_id import CustomTargetInfoFactory
from shellcheck_lib.help.program_modes.test_case.contents.main import overview as overview_content
from shellcheck_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.help.utils.table_of_contents import toc_list
from shellcheck_lib.util.std import StdOutputFiles
from shellcheck_lib.util.textformat.formatting.html import document as doc_rendering
from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.formatting.html.utils import ElementPopulator, ComplexElementPopulator
from shellcheck_lib.util.textformat.structure import core as doc
from shellcheck_lib.util.textformat.structure.document import SectionContents
from shellcheck_lib.util.textformat.structure.lists import ListType

PAGE_TITLE = '%s Reference Manual' % program_info.PROGRAM_NAME
TOC_TITLE = 'Table of Contents'

ELEMENT_STYLES = """\
pre {
background-color : #EEFFCC;
padding: 7px;
border: 1px solid #cEdFaC;
border-radius     : 3px;
}

h1 {
background-color: #E6E6FA;
border-radius     : 4px;
padding: 5px;
}

"""

TITLE_STYLE = """\
font-size: 250%;
font-weight: bold;
"""

TOC_TITLE_STYLE = """\
font-size: 200%;
font-weight: bold;
"""


class HtmlDocGenerator:
    def __init__(self,
                 output: StdOutputFiles,
                 application_help: ApplicationHelp):
        self.output = output
        self.application_help = application_help

    def apply(self):
        setup = self._setup()
        section_renderer = _section_renderer()
        renderer = doc_rendering.DocumentRenderer(section_renderer)
        contents = self._contents()
        renderer.apply(self.output.out, setup, contents)

    def _setup(self) -> doc_rendering.DocumentSetup:
        head_populator = StylePopulator(ELEMENT_STYLES)
        setup = doc_rendering.DocumentSetup(PAGE_TITLE,
                                            head_populator=head_populator,
                                            header_populator=HEADER_POPULATOR)
        return setup

    def _contents(self) -> SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, main_contents = self._main_contents(
            cross_ref.sub_component_factory('tc-overview',
                                            root_targets_factory))
        toc_paragraph = toc_list(target_info_hierarchy, ListType.ITEMIZED_LIST)
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


class DivWithTextAndStylePopulator(ElementPopulator):
    def __init__(self,
                 contents: str,
                 style: str):
        self.contents = contents
        self.style = style

    def apply(self, parent: Element):
        div = SubElement(parent, 'div')
        div.text = self.contents
        div.set('style', self.style)


class VersionPopulator(ElementPopulator):
    def apply(self, parent: Element):
        version = SubElement(parent, 'p')
        version.text = program_info.PROGRAM_NAME + ' version ' + program_info.VERSION
        SubElement(parent, 'hr')


HEADER_POPULATOR = ComplexElementPopulator([
    DivWithTextAndStylePopulator(PAGE_TITLE, TITLE_STYLE),
    VersionPopulator(),
    DivWithTextAndStylePopulator(TOC_TITLE, TOC_TITLE_STYLE),
])
