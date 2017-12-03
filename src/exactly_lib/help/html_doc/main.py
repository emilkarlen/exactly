from exactly_lib.help import std_tags
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.html_doc import page_setup
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.html_doc.parts import help
from exactly_lib.help.html_doc.parts import test_case
from exactly_lib.help.html_doc.parts import test_suite
from exactly_lib.help.program_modes.test_case.contents import cli_syntax as case_cli_syntax
from exactly_lib.help.program_modes.test_suite.contents import cli_syntax as suite_cli_syntax
from exactly_lib.help.render.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help_texts.cross_ref.custom_target_info_factory import root_factory
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.help_texts.entity.all_entity_types import ALL_ENTITY_TYPES_IN_DISPLAY_ORDER, \
    SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import parent
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    HierarchyGeneratorEnvironment, \
    SectionItemGeneratorNode, SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.table_of_contents import toc_list
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoNode
from exactly_lib.util.textformat.rendering.html import document as doc_rendering
from exactly_lib.util.textformat.rendering.html import text
from exactly_lib.util.textformat.rendering.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from exactly_lib.util.textformat.rendering.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.utils import section_item_contents_as_section_contents

_TEST_SUITES_HEADER = 'Test Suites'

_TEST_CASES_HEADER = 'Test Cases'


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
    hierarchy_environment = HierarchyGeneratorEnvironment({std_tags.TOC_SECTION})
    rendering_environment = ConstructionEnvironment(CrossReferenceTextConstructor(),
                                                    construct_simple_header_value_lists_as_tables=True)
    section_item = section_node.section_item(hierarchy_environment, rendering_environment)
    ret_val = section_item_contents_as_section_contents(section_item)
    _add_toc_as_first_paragraphs(ret_val, section_node.target_info_node())
    return ret_val


def _generator(application_help: ApplicationHelp) -> SectionHierarchyGenerator:
    return parent(
        page_setup.PAGE_TITLE,
        [],
        (
            _case_and_suite_sections(application_help)
            +
            _entity_sections(application_help,
                             entity_types_to_exclude=[SUITE_REPORTER_ENTITY_TYPE_NAMES.identifier])
            +
            _cli_syntax_sections('cli-syntax')
        ),
    )


def _case_and_suite_sections(application_help: ApplicationHelp) -> list:
    return [
        (
            'test-case',
            test_case.generator(_TEST_CASES_HEADER,
                                application_help.test_case_help,
                                )
        ),
        (
            'test-suite',
            test_suite.generator(_TEST_SUITES_HEADER,
                                 application_help.test_suite_help,
                                 application_help.entity_type_conf_for(
                                     SUITE_REPORTER_ENTITY_TYPE_NAMES.identifier))
        ),
    ]


def _entity_sections(application_help: ApplicationHelp,
                     entity_types_to_exclude: list) -> list:
    all_entity_type_names = filter(
        lambda
            etn: etn.identifier not in entity_types_to_exclude,
        ALL_ENTITY_TYPES_IN_DISPLAY_ORDER)

    def _section_setup_for_entity(names: EntityTypeNames) -> tuple:
        return (
            names.identifier,
            application_help.entity_type_conf_for(names.identifier).get_hierarchy_generator(
                names.name.plural.capitalize()),

        )

    return [
        _section_setup_for_entity(etn)
        for etn in all_entity_type_names
    ]


def _cli_syntax_sections(local_target_name: str) -> list:
    return [
        (
            local_target_name,
            parent('Command line syntax',
                   [],
                   [
                       ('test-case',
                        case_cli_syntax.generator(_TEST_CASES_HEADER)
                        ),
                       ('test-suite',
                        suite_cli_syntax.generator(_TEST_SUITES_HEADER)
                        ),
                       ('help',
                        help.generator('Getting Help')
                        ),
                   ]
                   )
        )
    ]


def _section_rendering_node(application_help: ApplicationHelp) -> SectionItemGeneratorNode:
    section_generator = _generator(application_help)
    return section_generator.generator_node(root_factory())


def _add_toc_as_first_paragraphs(contents: doc.SectionContents,
                                 target_info_node: TargetInfoNode):
    target_info_hierarchy = target_info_node.children
    toc_paragraph = toc_list(target_info_hierarchy, lists.ListType.ITEMIZED_LIST)
    contents.initial_paragraphs.insert(0, toc_paragraph)


def _section_renderer() -> doc_rendering.SectionItemRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionItemRenderer(target_renderer, section_header_renderer, paragraph_item_renderer)


def _page_setup() -> doc_rendering.DocumentSetup:
    head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
    return doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                       head_populator=head_populator,
                                       header_populator=page_setup.HEADER_POPULATOR)


def _html_doc_renderer() -> doc_rendering.DocumentRenderer:
    return doc_rendering.DocumentRenderer(_section_renderer())
