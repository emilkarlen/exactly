from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.concepts.concept_structure import ConceptDocumentation
from exactly_lib.help.concepts.render import IndividualConceptRenderer
from exactly_lib.help.contents_structure import ApplicationHelp
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.html_doc import page_setup
from exactly_lib.help.html_doc.cross_ref_target_renderer import HtmlTargetRenderer
from exactly_lib.help.program_modes.test_case.contents.main import overview as test_case_overview_rendering
from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseDocumentation
from exactly_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.test_case.render.render_instruction import InstructionManPageRenderer
from exactly_lib.help.program_modes.test_suite import render as test_suite_rendering
from exactly_lib.help.utils.cross_reference import CrossReferenceTextConstructor
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.help.utils.table_of_contents import toc_list
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.textformat.formatting.html import document as doc_rendering
from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.formatting.html.paragraph_item.full_paragraph_item import FullParagraphItemRenderer
from exactly_lib.util.textformat.formatting.html.section import HnSectionHeaderRenderer
from exactly_lib.util.textformat.structure import document  as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures  as docs


class HtmlDocGenerator:
    def __init__(self,
                 output: StdOutputFiles,
                 application_help: ApplicationHelp):
        self.output = output
        self.application_help = application_help
        self.rendering_environment = RenderingEnvironment(CrossReferenceTextConstructor())

    def apply(self):
        setup = self._page_setup()
        contents = self._contents()
        section_renderer = _section_renderer()
        renderer = doc_rendering.DocumentRenderer(section_renderer)
        renderer.apply(self.output.out, setup, contents)

    def _page_setup(self) -> doc_rendering.DocumentSetup:
        head_populator = page_setup.StylePopulator(page_setup.ELEMENT_STYLES)
        setup = doc_rendering.DocumentSetup(page_setup.PAGE_TITLE,
                                            head_populator=head_populator,
                                            header_populator=page_setup.HEADER_POPULATOR)
        return setup

    def _contents(self) -> doc.SectionContents:
        root_targets_factory = CustomTargetInfoFactory('')
        target_info_hierarchy, ret_val_contents = self._main_contents(root_targets_factory)
        toc_paragraph = toc_list(target_info_hierarchy, lists.ListType.ITEMIZED_LIST)
        ret_val_contents.initial_paragraphs.insert(0, toc_paragraph)
        return ret_val_contents

    def _main_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        test_case_targets_factory = cross_ref.sub_component_factory('test-case',
                                                                    targets_factory)
        test_case_target = test_case_targets_factory.root('Test Cases')
        test_case_sub_targets, test_case_contents = self._test_case_contents(test_case_targets_factory)

        test_suite_targets_factory = cross_ref.sub_component_factory('test-suite',
                                                                     targets_factory)
        test_suite_target = test_suite_targets_factory.root('Test Suites (TODO)')
        test_suite_sub_targets, test_suite_contents = self._test_suite_contents(test_suite_targets_factory)

        concepts_targets_factory = cross_ref.sub_component_factory('concepts',
                                                                   targets_factory)
        concepts_target = concepts_targets_factory.root('Concepts')
        concepts_sub_targets, concepts_contents = self._concepts_contents(concepts_targets_factory)

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(test_case_target.anchor_text(),
                            test_case_contents),
                doc.Section(test_suite_target.anchor_text(),
                            test_suite_contents),
                doc.Section(concepts_target.anchor_text(),
                            concepts_contents)
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(test_case_target,
                                     test_case_sub_targets),
            cross_ref.TargetInfoNode(test_suite_target,
                                     test_suite_sub_targets),
            cross_ref.TargetInfoNode(concepts_target,
                                     concepts_sub_targets),
        ]
        return ret_val_targets, ret_val_contents

    def _test_case_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        overview_targets_factory = cross_ref.sub_component_factory('overview',
                                                                   targets_factory)
        overview_target = overview_targets_factory.root('Test Case Overview')
        overview_sub_targets, overview_contents = self._test_case_overview_contents(overview_targets_factory)

        phases_targets_factory = cross_ref.sub_component_factory('phases',
                                                                 targets_factory)
        phases_target = phases_targets_factory.root('Phases')
        phases_sub_targets, phases_contents = self._test_case_phases_contents(phases_targets_factory)

        instructions_targets_factory = cross_ref.sub_component_factory('instructions',
                                                                       targets_factory)
        instructions_target = instructions_targets_factory.root('Instructions')
        instructions_sub_targets, instructions_contents = self._test_case_instructions_contents(
            instructions_targets_factory)

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(overview_target.anchor_text(),
                            overview_contents),
                doc.Section(phases_target.anchor_text(),
                            phases_contents),
                doc.Section(instructions_target.anchor_text(),
                            instructions_contents),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(overview_target,
                                     overview_sub_targets),
            cross_ref.TargetInfoNode(phases_target,
                                     phases_sub_targets),
            cross_ref.TargetInfoNode(instructions_target,
                                     instructions_sub_targets),
        ]
        return ret_val_targets, ret_val_contents

    def _test_case_overview_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = test_case_overview_rendering.OverviewRenderer(self.application_help.test_case_help,
                                                                  targets_factory)
        section_contents = generator.apply(self.rendering_environment)
        return generator.target_info_hierarchy(), section_contents

    def _test_case_phases_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for phase in self.application_help.test_case_help.phase_helps_in_order_of_execution:
            assert isinstance(phase, TestCasePhaseDocumentation)
            phase_presentation_str = phase.name.syntax
            cross_reference_target = cross_ref.TestCasePhaseCrossReference(phase.name.plain)
            header = docs.anchor_text(docs.text(phase_presentation_str),
                                      cross_reference_target)
            section = doc.Section(header,
                                  phase.render(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(phase_presentation_str,
                                                                             cross_reference_target),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)

    def _test_case_instructions_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for phase in self.application_help.test_case_help.phase_helps_in_order_of_execution:
            assert isinstance(phase, TestCasePhaseDocumentation)
            if not phase.is_phase_with_instructions:
                continue
            phase_target_factory = cross_ref.sub_component_factory(phase.name.plain,
                                                                   targets_factory)
            phase_presentation_str = phase.name.syntax
            phase_target = phase_target_factory.root(phase_presentation_str)
            phase_instruction_sections = []
            phase_instruction_targets = []
            for instruction_doc in phase.instruction_set.instruction_descriptions:
                # TODO refactor this into separate method
                assert isinstance(instruction_doc, InstructionDocumentation)
                instruction_cross_ref_target = cross_ref.TestCasePhaseInstructionCrossReference(
                    phase.name.plain,
                    instruction_doc.instruction_name())
                header = docs.anchor_text(docs.text(instruction_doc.instruction_name()),
                                          instruction_cross_ref_target)
                man_page_renderer = InstructionManPageRenderer(instruction_doc)
                instruction_section_contents = man_page_renderer.apply(self.rendering_environment)
                instruction_section = doc.Section(header,
                                                  instruction_section_contents)
                instruction_target_info = cross_ref.TargetInfoNode(
                    cross_ref.TargetInfo(instruction_doc.instruction_name(),
                                         instruction_cross_ref_target),
                    [])
                phase_instruction_sections.append(instruction_section)
                phase_instruction_targets.append(instruction_target_info)
            phase_section = doc.Section(phase_target.anchor_text(),
                                        doc.SectionContents([],
                                                            phase_instruction_sections))
            phase_target_info_node = cross_ref.TargetInfoNode(phase_target,
                                                              phase_instruction_targets)
            ret_val_targets.append(phase_target_info_node)
            ret_val_sections.append(phase_section)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)

    def _test_suite_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        generator = test_suite_rendering.OverviewRenderer(self.application_help.test_suite_help)
        section_contents = generator.apply(self.rendering_environment)
        return [], section_contents

    def _concepts_contents(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for concept in sorted(self.application_help.concepts_help.all_concepts,
                              key=lambda cn: cn.name().singular):
            assert isinstance(concept, ConceptDocumentation)
            concept_presentation_str = concept.name().singular
            header = docs.anchor_text(docs.text(concept_presentation_str),
                                      concept.cross_reference_target())
            section = doc.Section(header,
                                  IndividualConceptRenderer(concept).apply(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(concept_presentation_str,
                                                                             concept.cross_reference_target()),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)


def _section_renderer() -> doc_rendering.SectionRenderer:
    target_renderer = HtmlTargetRenderer()
    text_renderer = text.TextRenderer(target_renderer)
    section_header_renderer = HnSectionHeaderRenderer(text_renderer)
    paragraph_item_renderer = FullParagraphItemRenderer(text_renderer)
    return doc_rendering.SectionRenderer(section_header_renderer, paragraph_item_renderer)
