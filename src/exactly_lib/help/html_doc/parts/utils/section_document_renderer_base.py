from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.render_instruction import InstructionManPageRenderer
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.section_hierarchy_rendering import SectionRendererNode, \
    SectionRendererNodeWithSubSections, LeafSectionRendererNode, SectionGenerator
from exactly_lib.util.textformat.structure import document  as doc
from exactly_lib.util.textformat.structure import structures  as docs


class HtmlDocGeneratorForSectionDocumentBase:
    def __init__(self,
                 rendering_environment: RenderingEnvironment):
        self.rendering_environment = rendering_environment

    def sections_renderer_node(self,
                               header: str,
                               targets_factory: CustomTargetInfoFactory,
                               sections: list) -> SectionRendererNode:
        root_target_info = targets_factory.root(header)
        sub_section_nodes = []
        for phase in sections:
            assert isinstance(phase, SectionDocumentation)
            phase_presentation_str = phase.name.syntax
            cross_reference_target = self._section_cross_ref_target(phase)
            section_target_info = cross_ref.TargetInfo(phase_presentation_str,
                                                       cross_reference_target)
            section_node = LeafSectionRendererNode(section_target_info,
                                                   SectionContentsRendererForSectionDocumentSection(phase))
            sub_section_nodes.append(section_node)
        return SectionRendererNodeWithSubSections(root_target_info,
                                                  [],
                                                  sub_section_nodes)

    def _instructions_contents(self, targets_factory: CustomTargetInfoFactory,
                               sections: list) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for section in sections:
            assert isinstance(section, SectionDocumentation)
            if not section.has_instructions:
                continue
            phase_target_factory = cross_ref.sub_component_factory(section.name.plain,
                                                                   targets_factory)
            phase_presentation_str = section.name.syntax
            phase_target = phase_target_factory.root(phase_presentation_str)
            phase_instruction_sections = []
            phase_instruction_targets = []
            for instruction_doc in section.instruction_set.instruction_descriptions:
                assert isinstance(instruction_doc, InstructionDocumentation)
                instr_section, instr_target_info = self._instruction_documentation(instruction_doc,
                                                                                   section)
                phase_instruction_sections.append(instr_section)
                phase_instruction_targets.append(instr_target_info)
            phase_section = doc.Section(phase_target.anchor_text(),
                                        doc.SectionContents([],
                                                            phase_instruction_sections))
            phase_target_info_node = cross_ref.TargetInfoNode(phase_target,
                                                              phase_instruction_targets)
            ret_val_targets.append(phase_target_info_node)
            ret_val_sections.append(phase_section)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)

    def _instruction_documentation(self,
                                   instruction_doc: InstructionDocumentation,
                                   section: SectionDocumentation):
        instruction_cross_ref_target = self._instruction_cross_ref_target(instruction_doc, section)
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
        return instruction_section, instruction_target_info

    def _section_cross_ref_target(self, phase) -> CrossReferenceId:
        raise NotImplementedError()

    def _instruction_cross_ref_target(self, instruction_doc, section) -> CrossReferenceId:
        raise NotImplementedError()


def generator_for_sections(header: str,
                           sections: list,
                           doc: HtmlDocGeneratorForSectionDocumentBase) -> SectionGenerator:
    return _GeneratorForSections(header, sections, doc)


class _GeneratorForSections(SectionGenerator):
    def __init__(self,
                 header: str,
                 sections: list,
                 doc_generator: HtmlDocGeneratorForSectionDocumentBase):
        self.header = header
        self.sections = sections
        self.doc_generator = doc_generator

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        return self.doc_generator.sections_renderer_node(self.header, target_factory, self.sections)


class SectionContentsRendererForSectionDocumentSection(SectionContentsRenderer):
    def __init__(self, section_documentation: SectionDocumentation):
        self.section_documentation = section_documentation

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.section_documentation.render(environment)
