from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.html_doc import page_setup
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.html_doc.parts import help
from exactly_lib.help.html_doc.parts import test_case
from exactly_lib.help.html_doc.parts import test_suite
from exactly_lib.help.html_doc.parts.utils import entities_list_renderer
from exactly_lib.help.utils.rendering.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator, parent, \
    SectionRendererNode
from exactly_lib.help.utils.table_of_contents import toc_list
from exactly_lib.help_texts import entity_names
from exactly_lib.help_texts.cross_reference_id import root_factory, TargetInfoNode
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
    contents = section_contents(application_help)
    html_doc_renderer = _html_doc_renderer()
    setup = _page_setup()
    html_doc_renderer.apply(output_file, setup, contents)


def section_contents(application_help: ApplicationHelp) -> doc.SectionContents:
    section_node = _section_rendering_node(application_help)

    rendering_environment = RenderingEnvironment(CrossReferenceTextConstructor(),
                                                 render_simple_header_value_lists_as_tables=True)
    ret_val = section_node.section(rendering_environment).contents
    _add_toc_as_first_paragraphs(ret_val, section_node.target_info_node())
    return ret_val


def _generator(application_help: ApplicationHelp) -> SectionHierarchyGenerator:
    return parent(
        page_setup.PAGE_TITLE,
        [],
        [
            (
                'test-case',
                test_case.generator('Test Cases',
                                    application_help.test_case_help,
                                    application_help.entity_conf_for(entity_names.ACTOR_ENTITY_TYPE_NAME),
                                    application_help.entity_conf_for(entity_names.TYPE_ENTITY_TYPE_NAME),
                                    )
            ),
            (
                'test-suite',
                test_suite.generator('Test Suites', application_help.test_suite_help,
                                     application_help.entity_conf_for(entity_names.SUITE_REPORTER_ENTITY_TYPE_NAME))
            ),
            (
                'concepts',
                entities_list_renderer.hierarchy_generator(
                    'Concepts',
                    application_help.entity_conf_for(entity_names.CONCEPT_ENTITY_TYPE_NAME)),
            ),
            (
                'help',
                help.generator('Getting Help')
            ),
        ],

    )


def _section_rendering_node(application_help: ApplicationHelp) -> SectionRendererNode:
    section_generator = _generator(application_help)
    return section_generator.section_renderer_node(root_factory())


def _add_toc_as_first_paragraphs(contents: doc.SectionContents,
                                 target_info_node: TargetInfoNode):
    target_info_hierarchy = target_info_node.children
    toc_paragraph = toc_list(target_info_hierarchy, lists.ListType.ITEMIZED_LIST)
    contents.initial_paragraphs.insert(0, toc_paragraph)


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)


def _page_setup() -> doc_rendering.DocumentSetup:
    head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
    return doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                       head_populator=head_populator,
                                       header_populator=page_setup.HEADER_POPULATOR)


def _html_doc_renderer() -> doc_rendering.DocumentRenderer:
    html_section_renderer = _section_renderer()
    html_doc_renderer = doc_rendering.DocumentRenderer(html_section_renderer)
    return html_doc_renderer
