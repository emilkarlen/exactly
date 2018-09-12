from typing import Sequence, List, Callable

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.help import std_tags
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation, InstructionGroup
from exactly_lib.help.program_modes.common.render_instruction import InstructionDocArticleContentsConstructor
from exactly_lib.util.textformat.construction.section_contents_constructor import ArticleContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionItemGeneratorNode, \
    SectionHierarchyGenerator, LeafArticleGeneratorNode, SectionItemGeneratorNodeWithSubSections
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CustomTargetInfoFactory
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import StringText, ParagraphItem

_INSTRUCTIONS_IN = 'The instructions in the {section} {section_concept}.'


class HtmlDocGeneratorForSectionDocumentBase:
    def __init__(self,
                 section_concept_name: str,
                 sections: Sequence[SectionDocumentation],
                 get_article_contents_constructor: Callable[[SectionDocumentation], ArticleContentsConstructor]):
        self.section_concept_name = section_concept_name
        self.sections = sections
        self.get_article_contents_constructor = get_article_contents_constructor

    def _section_cross_ref_target(self, section: SectionDocumentation) -> CrossReferenceId:
        raise NotImplementedError()

    def _instruction_cross_ref_target(self,
                                      instruction: InstructionDocumentation,
                                      section: SectionDocumentation) -> CrossReferenceId:
        raise NotImplementedError()

    def generator_for_sections(self, header: str) -> SectionHierarchyGenerator:
        return _SectionsListGenerator(header, self.sections, self)

    def generator_for_custom_sections(self,
                                      header: str,
                                      sections: Sequence[SectionDocumentation]) -> SectionHierarchyGenerator:
        return _SectionsListGenerator(header, sections, self)

    def generator_for_instructions_per_section(self, header: str) -> SectionHierarchyGenerator:
        super_self = self

        class _HierarchyGenerator(SectionHierarchyGenerator):
            def generator_node(self, target_factory: targets.CustomTargetInfoFactory
                               ) -> SectionItemGeneratorNode:
                return super_self._instructions_per_section_node(header, target_factory)

        return _HierarchyGenerator()

    def _instructions_per_section_node(self,
                                       header: str,
                                       targets_factory: targets.CustomTargetInfoFactory
                                       ) -> SectionItemGeneratorNode:
        root_target_info = targets_factory.root(StringText(header))
        section_nodes = []
        for section in self.sections:
            assert isinstance(section, SectionDocumentation)
            if not section.has_instructions:
                continue
            instructions_node_constructor = _SectionInstructionsNodeConstructor(
                self.section_concept_name,
                self._instruction_cross_ref_target,
                targets_factory.sub_factory(section.name.plain),
                section)
            section_nodes.append(instructions_node_constructor())
        return SectionItemGeneratorNodeWithSubSections(root_target_info,
                                                       [],
                                                       section_nodes)


class _SectionInstructionsNodeConstructor:
    def __init__(self,
                 section_concept_name: str,
                 mk_instruction_cross_ref_target: Callable[
                     [InstructionDocumentation, SectionDocumentation], CrossReferenceId],
                 section_target_factory: CustomTargetInfoFactory,
                 section: SectionDocumentation
                 ):

        self.section_concept_name = section_concept_name
        self.mk_instruction_cross_ref_target = mk_instruction_cross_ref_target
        self.section_target_factory = section_target_factory
        self.section = section

    def __call__(self) -> SectionItemGeneratorNode:
        return SectionItemGeneratorNodeWithSubSections(
            self.section_target_factory.root(self.section.syntax_name_text),
            self._initial_paras(),
            self._instructions_sub_nodes())

    def _initial_paras(self) -> List[ParagraphItem]:
        return docs.paras(_INSTRUCTIONS_IN.format(
            section_concept=self.section_concept_name,
            section=self.section.name)
        )

    def _instructions_sub_nodes(self) -> Sequence[SectionItemGeneratorNode]:
        instr_docs = self.section.instruction_set.instruction_documentations
        if self.section.instruction_group_by:
            return self._instruction_group_nodes(self.section.instruction_group_by.__call__(instr_docs))
        else:
            return self._instruction_nodes(instr_docs)

    def _instruction_nodes(self,
                           instructions: Sequence[InstructionDocumentation]) -> List[SectionItemGeneratorNode]:
        return [
            self._instruction_node(instruction)
            for instruction in instructions
        ]

    def _instruction_group_nodes(self, groups: Sequence[InstructionGroup]) -> List[SectionItemGeneratorNode]:
        return list(map(self._instruction_group_node, groups))

    def _instruction_group_node(self, group: InstructionGroup) -> SectionItemGeneratorNode:
        return SectionItemGeneratorNodeWithSubSections(
            self.section_target_factory.sub_factory(group.identifier).root(StringText(group.header)),
            group.description_paragraphs,
            self._instruction_nodes(group.instruction_documentations))

    def _instruction_node(self, instruction: InstructionDocumentation) -> SectionItemGeneratorNode:
        cross_ref_target = self.mk_instruction_cross_ref_target(instruction, self.section)
        target_info = targets.TargetInfo(instruction.instruction_name_text,
                                         cross_ref_target)
        return LeafArticleGeneratorNode(target_info,
                                        InstructionDocArticleContentsConstructor(instruction),
                                        tags={std_tags.INSTRUCTION})


class _SectionsListGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 header: str,
                 sections: Sequence[SectionDocumentation],
                 conf: HtmlDocGeneratorForSectionDocumentBase):
        self._conf = conf
        self._sections = sections
        self._header = header

    def generator_node(self, target_factory: targets.CustomTargetInfoFactory
                       ) -> SectionItemGeneratorNode:
        root_target_info = target_factory.root(docs.string_text(self._header))
        sub_section_nodes = []
        for section in self._sections:
            cross_reference_target = self._conf._section_cross_ref_target(section)
            section_target_info = targets.TargetInfo(section.syntax_name_text,
                                                     cross_reference_target)
            section_node = LeafArticleGeneratorNode(
                section_target_info,
                self._conf.get_article_contents_constructor(section),
                tags={std_tags.SECTION})
            sub_section_nodes.append(section_node)

        return SectionItemGeneratorNodeWithSubSections(root_target_info,
                                                       [],
                                                       sub_section_nodes)
