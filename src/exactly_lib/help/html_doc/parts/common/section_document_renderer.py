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
        return h.hierarchy(
            header,
            paragraphs.empty(),
            [
                h.child(section.name.plain,
                        h.with_fixed_root_target(
                            section.section_info.cross_reference_target,
                            h.leaf_article(
                                section.syntax_name_text,
                                self._article_constructor_for_section(section),
                                tags={std_tags.SECTION},
                            )
                        ),
                        )
                for section in sections
            ]
        )

    def instructions_per_section(self,
                                 header: str,
                                 ) -> SectionHierarchyGenerator:
        return h.hierarchy(header,
                           paragraphs.empty(),
                           [
                               h.child(section.name.plain,
                                       _InstructionsInSection.hierarchy_for(self._section_concept_name,
                                                                            section),
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

    @staticmethod
    def hierarchy_for(section_concept_name: str,
                      section: SectionDocumentation
                      ) -> SectionHierarchyGenerator:
        return _InstructionsInSection(section_concept_name,
                                      section).hierarchy()

    def hierarchy(self) -> SectionHierarchyGenerator:
        initial_paragraphs = paragraphs.constant(
            docs.paras(_INSTRUCTIONS_IN.format(
                section_concept=self.section_concept_name,
                section=self.section.name)
            ))
        return h.hierarchy(self.section.syntax_name_text,
                           initial_paragraphs,
                           self._instructions_layout(),
                           )

    def _instructions_layout(self) -> List[SectionHierarchyGenerator]:
        instructions = self.section.instruction_set.instruction_documentations
        if self.section.instruction_group_by:
            return self._instruction_groups(self.section.instruction_group_by.__call__(instructions))
        else:
            return self._instructions(instructions)

    def _instruction_groups(self, groups: Sequence[InstructionGroup]) -> List[SectionHierarchyGenerator]:
        return [
            h.child_hierarchy(group.identifier,
                              group.header,
                              paragraphs.constant(group.description_paragraphs),
                              self._instructions(group.instruction_documentations)
                              )
            for group in groups
        ]

    def _instructions(self, instructions: Sequence[InstructionDocumentation]) -> List[SectionHierarchyGenerator]:
        return [
            self._instruction(instruction)
            for instruction in instructions
        ]

    def _instruction(self, instruction: InstructionDocumentation) -> SectionHierarchyGenerator:
        return h.with_fixed_root_target(
            self.section.section_info.instruction_cross_reference_target(instruction.instruction_name()),
            h.leaf_article(
                instruction.instruction_name_text,
                InstructionDocArticleContentsConstructor(instruction),
                tags={std_tags.INSTRUCTION},
            )
        )
