from exactly_lib.help_texts import cross_reference_id
from exactly_lib.help_texts.formatting import AnyInstructionNameDictionary
from exactly_lib.help_texts.test_case.phase_names import phase_name_dict_key_for, \
    PHASE_NAME_DICTIONARY
from exactly_lib.help_texts.test_suite.formatted_section_names import suite_section_name_dictionary, \
    suite_section_name_dict_key_for
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText, UrlCrossReferenceTarget, StringText, \
    CrossReferenceTarget


class CrossReferenceTextConstructor(targets.CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceTarget) -> Text:
        return CrossReferenceText(StringText(_TITLE_RENDERER.visit(x)), x)


class _TitleRenderer(cross_reference_id.CrossReferenceIdVisitor):
    def __init__(self):
        self.any_instruction = AnyInstructionNameDictionary()
        self.suite_section_name_dict = suite_section_name_dictionary()

    def visit_custom(self, x: cross_reference_id.CustomCrossReferenceId) -> str:
        raise ValueError('Rendering of custom cross references is not supported ("%s")' %
                         x.target_name)

    def visit_url(self, x: UrlCrossReferenceTarget) -> str:
        raise ValueError('Rendering of url cross references is not supported ("%s")' %
                         x.url)

    def visit_test_case_phase(self, x: cross_reference_id.TestCasePhaseCrossReference
                              ) -> str:
        return 'Phase %s' % PHASE_NAME_DICTIONARY[phase_name_dict_key_for(x.phase_name)].syntax

    def visit_test_case_phase_instruction(self, x: cross_reference_id.TestCasePhaseInstructionCrossReference
                                          ) -> str:
        return 'Instruction {i} (in phase {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=PHASE_NAME_DICTIONARY[phase_name_dict_key_for(x.phase_name)].syntax)

    def visit_test_suite_section(self, x: cross_reference_id.TestSuiteSectionCrossReference
                                 ) -> str:
        return 'Suite section %s' % self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax

    def visit_test_suite_section_instruction(self, x: cross_reference_id.TestSuiteSectionInstructionCrossReference
                                             ) -> str:
        return 'Suite instruction {i} (in section {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax)

    def visit_entity(self, x: cross_reference_id.EntityCrossReferenceId
                     ) -> str:
        return x.entity_type_presentation_name.capitalize() + ' "' + x.entity_name + '"'


_TITLE_RENDERER = _TitleRenderer()
