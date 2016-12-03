from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.concepts.render import IndividualConceptRenderer
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.html_doc import page_setup
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.html_doc.parts.help import HtmlDocGeneratorForHelpHelp
from exactly_lib.help.html_doc.parts.test_case import HtmlDocGeneratorForTestCaseHelp
from exactly_lib.help.html_doc.parts.test_suite import HtmlDocGeneratorForTestSuiteHelp
from exactly_lib.help.html_doc.parts.utils.entities_list_renderer import HtmlDocGeneratorForEntitiesHelp
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.help.utils.table_of_contents import toc_list
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.textformat.formatting.html import document as doc_rendering
from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from exactly_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists


class HtmlDocGenerator:
    def __init__(self,
                 output: StdOutputFiles,
                 application_help: ApplicationHelp):
        self.output = output
        self.renderer = HtmlDocContentsRenderer(application_help)

    def apply(self):
        setup = self._page_setup()
        contents = self.renderer.apply()
        section_renderer = _section_renderer()
        renderer = doc_rendering.DocumentRenderer(section_renderer)
        renderer.apply(self.output.out, setup, contents)

    def _page_setup(self) -> doc_rendering.DocumentSetup:
        head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
        setup = doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                            head_populator=head_populator,
                                            header_populator=page_setup.HEADER_POPULATOR)
        return setup


class HtmlDocContentsRenderer:
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help
        rendering_environment = RenderingEnvironment(CrossReferenceTextConstructor(),
                                                     render_simple_header_value_lists_as_tables=True)
        self.test_case_generator = HtmlDocGeneratorForTestCaseHelp(rendering_environment,
                                                                   application_help.test_case_help)
        self.test_suite_generator = HtmlDocGeneratorForTestSuiteHelp(rendering_environment,
                                                                     application_help.test_suite_help)
        self.concepts_generator = HtmlDocGeneratorForEntitiesHelp(IndividualConceptRenderer,
                                                                  application_help.concepts_help.all_entities,
                                                                  rendering_environment)
        self.help_generator = HtmlDocGeneratorForHelpHelp(rendering_environment)

    def apply(self) -> doc.SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, ret_val_contents = self._main_contents(root_targets_factory)
        toc_paragraph = toc_list(target_info_hierarchy, lists.ListType.ITEMIZED_LIST)
        ret_val_contents.initial_paragraphs.insert(0, toc_paragraph)
        return ret_val_contents

    def _main_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        test_case_targets_factory = cross_ref.sub_component_factory('test-case',
                                                                    targets_factory)
        test_case_target = test_case_targets_factory.root('Test Cases')
        test_case_sub_targets, test_case_contents = self.test_case_generator.apply(test_case_targets_factory)

        test_suite_targets_factory = cross_ref.sub_component_factory('test-suite',
                                                                     targets_factory)
        test_suite_target = test_suite_targets_factory.root('Test Suites')
        test_suite_sub_targets, test_suite_contents = self.test_suite_generator.apply(test_suite_targets_factory)

        concepts_targets_factory = cross_ref.sub_component_factory('concepts',
                                                                   targets_factory)
        concepts_target = concepts_targets_factory.root('Concepts')
        concepts_sub_targets, concepts_contents = self.concepts_generator.apply(concepts_targets_factory)

        help_targets_factory = cross_ref.sub_component_factory('help',
                                                               targets_factory)
        help_target = help_targets_factory.root('Getting Help')
        help_sub_targets, help_contents = self.help_generator.apply(help_targets_factory)

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(test_case_target.anchor_text(),
                            test_case_contents),
                doc.Section(test_suite_target.anchor_text(),
                            test_suite_contents),
                doc.Section(concepts_target.anchor_text(),
                            concepts_contents),
                doc.Section(help_target.anchor_text(),
                            help_contents),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(test_case_target,
                                     test_case_sub_targets),
            cross_ref.TargetInfoNode(test_suite_target,
                                     test_suite_sub_targets),
            cross_ref.TargetInfoNode(concepts_target,
                                     concepts_sub_targets),
            cross_ref.TargetInfoNode(help_target,
                                     help_sub_targets),
        ]
        return ret_val_targets, ret_val_contents


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)
