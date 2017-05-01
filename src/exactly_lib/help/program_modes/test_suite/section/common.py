from exactly_lib.common.help.cross_reference_id import TestSuiteSectionInstructionCrossReference
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import instruction_set_list
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.see_also_section import see_also_sections
from exactly_lib.help_texts.names.formatting import SectionName
from exactly_lib.help_texts.test_suite.section_names import DEFAULT_SECTION_NAME
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import transform_list_to_table


class TestSuiteSectionDocumentationBase(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name, 'section')
        self._section_name = SectionName(name)

    def contents_description(self) -> list:
        """
        :return: [`ParagraphItem`]
        """
        raise NotImplementedError()

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        purpose = self.purpose()
        mandatory_info = self._mandatory_info_para()
        paras = ([docs.para(purpose.single_line_description)] +
                 purpose.rest +
                 [mandatory_info] +
                 self._default_section_info(DEFAULT_SECTION_NAME))
        sections = []
        self._add_section_for_contents_description(sections)
        self._add_section_for_see_also(environment, sections)
        self._add_section_for_instructions(environment, sections)

        return doc.SectionContents(paras, sections)

    def _add_section_for_contents_description(self, output: list):
        output.append(docs.section('Contents',
                                   self.contents_description()))

    def _add_section_for_instructions(self,
                                      environment: RenderingEnvironment,
                                      output: list):
        if self.has_instructions:
            il = instruction_set_list(self.instruction_set, self._cross_ref_text)
            if environment.render_simple_header_value_lists_as_tables:
                il = transform_list_to_table(il)
            output.append(docs.section('Instructions', [il]))

    def _add_section_for_see_also(self, environment: RenderingEnvironment, sections: list):
        sections.extend(see_also_sections(self.see_also_items, environment))

    def _cross_ref_text(self, instr_name: str) -> docs.Text:
        return docs.cross_reference(instr_name,
                                    TestSuiteSectionInstructionCrossReference(self._section_name.plain,
                                                                              instr_name),
                                    allow_rendering_of_visible_extra_target_text=False)


class TestSuiteSectionDocumentationForSectionWithInstructions(TestSuiteSectionDocumentationBase):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(name)
        self._instruction_set = instruction_set

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return self._instruction_set

    def contents_description(self) -> list:
        return [docs.para('Consists of zero or more instructions.')] + self.instruction_purpose_description()

    def instruction_purpose_description(self) -> list:
        """
        :return: [ParagraphItem]
        """
        raise NotImplementedError()


class TestSuiteSectionDocumentationBaseForSectionWithoutInstructions(TestSuiteSectionDocumentationBase):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None
