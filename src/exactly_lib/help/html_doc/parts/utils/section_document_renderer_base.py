import types

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.render_instruction import InstructionManPageRenderer
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionRendererNode, \
    SectionRendererNodeWithSubSections, LeafSectionRendererNode, SectionGenerator
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.help_texts.name_and_cross_ref import CrossReferenceId


class HtmlDocGeneratorForSectionDocumentBase:
    def __init__(self,
                 sections: list,
                 get_section_contents_renderer_for_section_document: types.FunctionType):
        self.sections = sections
        self.get_section_contents_renderer_for_section_document = get_section_contents_renderer_for_section_document

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        raise NotImplementedError()

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        raise NotImplementedError()

    def generator_for_sections(self, header: str) -> SectionGenerator:
        super_self = self

        class _Generator(SectionGenerator):
            def section_renderer_node(self, target_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
                return super_self._sections_renderer_node(header, target_factory)

        return _Generator()

    def generator_for_instructions_per_section(self, header: str) -> SectionGenerator:
        super_self = self

        class _Generator(SectionGenerator):
            def section_renderer_node(self, target_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
                return super_self._instructions_per_section_node(header, target_factory)

        return _Generator()

    def _sections_renderer_node(self,
                                header: str,
                                targets_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
        root_target_info = targets_factory.root(header)
        sub_section_nodes = []
        for section in self.sections:
            assert isinstance(section, SectionDocumentation)
            phase_presentation_str = section.name.syntax
            cross_reference_target = self._section_cross_ref_target(section)
            section_target_info = cross_ref.TargetInfo(phase_presentation_str,
                                                       cross_reference_target)
            section_node = LeafSectionRendererNode(
                section_target_info,
                self.get_section_contents_renderer_for_section_document(section))
            sub_section_nodes.append(section_node)

        return SectionRendererNodeWithSubSections(root_target_info,
                                                  [],
                                                  sub_section_nodes)

    def _instructions_per_section_node(self,
                                       header: str,
                                       targets_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
        root_target_info = targets_factory.root(header)
        section_nodes = []
        for section in self.sections:
            assert isinstance(section, SectionDocumentation)
            if not section.has_instructions:
                continue
            section_target_factory = targets_factory.sub_factory(section.name.plain)
            section_target_info = section_target_factory.root(section.name.syntax)
            section_nodes.append(self._section_instructions_node(section_target_info,
                                                                 section))
        return SectionRendererNodeWithSubSections(root_target_info,
                                                  [],
                                                  section_nodes)

    def _section_instructions_node(self,
                                   section_target_info: cross_ref.TargetInfo,
                                   section: SectionDocumentation) -> SectionRendererNode:
        instruction_nodes = [
            self._instruction_node(instruction, section)
            for instruction in section.instruction_set.instruction_descriptions
        ]
        return SectionRendererNodeWithSubSections(section_target_info,
                                                  [],
                                                  instruction_nodes)

    def _instruction_node(self,
                          instruction: InstructionDocumentation,
                          section: SectionDocumentation) -> SectionRendererNode:
        cross_ref_target = self._instruction_cross_ref_target(instruction, section)
        target_info = cross_ref.TargetInfo(instruction.instruction_name(),
                                           cross_ref_target)
        return LeafSectionRendererNode(target_info,
                                       InstructionManPageRenderer(instruction))
