from shellcheck_lib.help import cross_reference_id as cross_ref
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.cross_reference_id import CustomTargetInfoFactory
from shellcheck_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from shellcheck_lib.help.html_doc import page_setup
from shellcheck_lib.help.program_modes.test_case.contents.main import overview as overview_content
from shellcheck_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.help.utils.table_of_contents import toc_list
from shellcheck_lib.util.std import StdOutputFiles
from shellcheck_lib.util.textformat.formatting.html import document as doc_rendering
from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from shellcheck_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from shellcheck_lib.util.textformat.structure.document import SectionContents
from shellcheck_lib.util.textformat.structure.lists import ListType


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
        head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
        setup = doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                            head_populator=head_populator,
                                            header_populator=page_setup.HEADER_POPULATOR)
        return setup

    def _contents(self) -> SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, ret_val_contents = self._main_contents(
            cross_ref.sub_component_factory('tc-overview',
                                            root_targets_factory))
        toc_paragraph = toc_list(target_info_hierarchy, ListType.ITEMIZED_LIST)
        ret_val_contents.initial_paragraphs.insert(0, toc_paragraph)
        return ret_val_contents

    def _main_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, SectionContents):
        generator = overview_content.OverviewRenderer(self.application_help.test_case_help,
                                                      targets_factory)
        cross_reference_text_constructor = CrossReferenceTextConstructor()
        environment = RenderingEnvironment(cross_reference_text_constructor)
        section_contents = generator.apply(environment)
        return generator.target_info_hierarchy(), section_contents


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)


