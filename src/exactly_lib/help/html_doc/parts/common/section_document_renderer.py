from typing import Sequence, List, Callable

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help import std_tags
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, InstructionGroup
from exactly_lib.help.program_modes.common.render_instruction import InstructionDocArticleContentsConstructor
from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import StringText

_INSTRUCTIONS_IN = 'The instructions in the {section} {section_concept}.'


class GeneratorsForSectionDocument:
    def __init__(self,
                 section_concept_name: str,
                 sections: Sequence[SectionDocumentation],
                 article_constructor_for_section: Callable[[SectionDocumentation], ArticleContentsConstructor]):
        self._section_concept_name = section_concept_name
        self._sections = sections
        self._article_constructor_for_section = article_constructor_for_section

    def all_sections_list(self, header: str) -> SectionHierarchyGenerator:
        return self.custom_sections_list(header, self._sections)

    def custom_sections_list(self,
                             header: str,
                             sections: Sequence[SectionDocumentation]) -> SectionHierarchyGenerator:
        return h.parent(
            header,
            paragraphs.empty(),
            [
                h.Node(section.name.plain,
                       h.leaf_article_with_constant_target(
                           section.syntax_name_text,
                           section.section_info.cross_reference_target,
                           self._article_constructor_for_section(section),
                           tags={std_tags.SECTION},
                       ),
                       )
                for section in sections
            ]
        )

    def instructions_per_section(self,
                                 header: str,
                                 ) -> SectionHierarchyGenerator:
        return h.parent3(StringText(header),
                         paragraphs.empty(),
                         [
                             h.Node(section.name.plain,
                                    _InstructionsInSection(self._section_concept_name,
                                                           section).generator(),
                                    )
                             for section in self._sections
                             if section.has_instructions
                         ])


class _InstructionsInSection:
    def __init__(self,
                 section_concept_name: str,
                 section: SectionDocumentation
                 ):

        self.section_concept_name = section_concept_name
        self.section = section

    def generator(self) -> SectionHierarchyGenerator:
        initial_paragraphs = paragraphs.constant(docs.paras(_INSTRUCTIONS_IN.format(
            section_concept=self.section_concept_name,
            section=self.section.name)
        ))
        return h.parent3(self.section.syntax_name_text,
                         initial_paragraphs,
                         self.instruction_generators(),
                         )

    def instruction_generators(self) -> List[h.Node]:
        instr_docs = self.section.instruction_set.instruction_documentations
        if self.section.instruction_group_by:
            return self._instruction_group_nodes(self.section.instruction_group_by.__call__(instr_docs))
        else:
            return self._instruction_nodes(instr_docs)

    def _instruction_group_nodes(self, groups: Sequence[InstructionGroup]) -> List[h.Node]:
        return [
            h.Node(group.identifier,
                   h.parent(group.header,
                            paragraphs.constant(group.description_paragraphs),
                            self._instruction_nodes(group.instruction_documentations)))
            for group in groups
        ]

    def _instruction_nodes(self, instructions: Sequence[InstructionDocumentation]) -> List[h.Node]:
        return [
            self._instruction_node(instruction)
            for instruction in instructions
        ]

    def _instruction_node(self, instruction: InstructionDocumentation) -> h.Node:
        # TODO Gör om t SectionHierarchyGenerator?
        cross_ref_target = self.section.section_info.instruction_cross_reference_target(instruction.instruction_name())

        return h.Node(instruction.instruction_name(),  # Unused local target
                      h.leaf_article_with_constant_target(
                          instruction.instruction_name_text,
                          cross_ref_target,
                          InstructionDocArticleContentsConstructor(instruction),
                          tags={std_tags.INSTRUCTION},
                      ))
