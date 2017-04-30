from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.concepts.render import IndividualConceptRenderer
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.html_doc import page_setup
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.html_doc.parts import help
from exactly_lib.help.html_doc.parts import test_case
from exactly_lib.help.html_doc.parts import test_suite
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.table_of_contents import toc_list
from exactly_lib.util.textformat.formatting.html import document as doc_rendering
from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from exactly_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists


def generate_and_output(output_file,
                        application_help: ApplicationHelp):
    """
    Outputs html-doc help on given file.
    """
    contents = HtmlDocContentsRenderer(application_help).apply()
    section_renderer = _section_renderer()
    renderer = doc_rendering.DocumentRenderer(section_renderer)
    setup = _page_setup()
    renderer.apply(output_file, setup, contents)


class HtmlDocContentsRenderer:
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help
        self.rendering_environment = RenderingEnvironment(CrossReferenceTextConstructor(),
                                                          render_simple_header_value_lists_as_tables=True)
        self.test_case_generator = test_case.generator('Test Cases', application_help.test_case_help)
        self.test_suite_generator = test_suite.generator('Test Suites', application_help.test_suite_help)
        self.concepts_generator = HtmlDocGeneratorForEntitiesHelp('Concepts',
                                                                  IndividualConceptRenderer,
                                                                  application_help.concepts_help.all_entities)
        self.help_generator = help.generator('Getting Help')

    def apply(self) -> doc.SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, ret_val_contents = self._main_contents(root_targets_factory)
        toc_paragraph = toc_list(target_info_hierarchy, lists.ListType.ITEMIZED_LIST)
        ret_val_contents.initial_paragraphs.insert(0, toc_paragraph)
        return ret_val_contents

    def _main_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        test_cases_node = self.test_case_generator.section_renderer_node(targets_factory.sub_factory('test-case'))

        test_suites_node = self.test_suite_generator.section_renderer_node(targets_factory.sub_factory('test-suite'))

        concepts_node = self.concepts_generator.section_renderer_node(targets_factory.sub_factory('concepts'))

        help_node = self.help_generator.section_renderer_node(targets_factory.sub_factory('help'))

        ret_val_contents = doc.SectionContents(
            [],
            [
                test_cases_node.section(self.rendering_environment),
                test_suites_node.section(self.rendering_environment),
                concepts_node.section(self.rendering_environment),
                help_node.section(self.rendering_environment),
            ]
        )
        ret_val_targets = [
            test_cases_node.target_info_node(),
            test_suites_node.target_info_node(),
            concepts_node.target_info_node(),
            help_node.target_info_node(),
        ]
        return ret_val_targets, ret_val_contents


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)


def _page_setup() -> doc_rendering.DocumentSetup:
    head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
    setup = doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                        head_populator=head_populator,
                                        header_populator=page_setup.HEADER_POPULATOR)
    return setup
