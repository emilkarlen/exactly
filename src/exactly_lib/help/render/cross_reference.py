from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref import concrete_cross_refs
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.formatting import AnyInstructionNameDictionary
from exactly_lib.definitions.test_case.phase_names import phase_name_dict_key_for, \
    PHASE_NAME_DICTIONARY
from exactly_lib.definitions.test_suite.section_names import suite_section_name_dictionary, \
    suite_section_name_dict_key_for
from exactly_lib.util.textformat.constructor import text
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText, UrlCrossReferenceTarget, StringText, \
    CrossReferenceTarget


class CrossReferenceTextConstructor(text.CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceTarget) -> Text:
        return CrossReferenceText(StringText(_TITLE_RENDERER.visit(x)), x)


class _TitleRenderer(concrete_cross_refs.CrossReferenceTargetVisitor):
    def __init__(self):
        self.any_instruction = AnyInstructionNameDictionary()
        self.suite_section_name_dict = suite_section_name_dictionary()

    def visit_custom(self, x: concrete_cross_refs.CustomCrossReferenceId) -> str:
        raise ValueError('Rendering of custom cross references is not supported ("%s")' %
                         x.target_name)

    def visit_url(self, x: UrlCrossReferenceTarget) -> str:
        raise ValueError('Rendering of url cross references is not supported ("%s")' %
                         x.url)

    def visit_test_case_phase(self, x: concrete_cross_refs.TestCasePhaseCrossReference
                              ) -> str:
        return 'Phase %s' % PHASE_NAME_DICTIONARY[phase_name_dict_key_for(x.phase_name)].syntax

    def visit_test_case_phase_instruction(self, x: concrete_cross_refs.TestCasePhaseInstructionCrossReference
                                          ) -> str:
        return 'Instruction {i} (in phase {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=PHASE_NAME_DICTIONARY[phase_name_dict_key_for(x.phase_name)].syntax)

    def visit_test_suite_section(self, x: concrete_cross_refs.TestSuiteSectionCrossReference
                                 ) -> str:
        return 'Suite section %s' % self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax

    def visit_test_suite_section_instruction(self, x: concrete_cross_refs.TestSuiteSectionInstructionCrossReference
                                             ) -> str:
        return 'Suite instruction {i} (in section {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax)

    def visit_entity(self, x: concrete_cross_refs.EntityCrossReferenceId
                     ) -> str:
        return x.entity_type_presentation_name.capitalize() + ' "' + x.entity_name + '"'

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference) -> str:
        return _PREDEFINED_PART_TITLE[x.part]


_TITLE_RENDERER = _TitleRenderer()

_PREDEFINED_PART_TITLE = {
    HelpPredefinedContentsPart.TEST_CASE_CLI: 'Test case CLI',
    HelpPredefinedContentsPart.TEST_SUITE_CLI: 'Test suite CLI',
    HelpPredefinedContentsPart.SYMBOL_CLI: 'Symbol usages information CLI',
    HelpPredefinedContentsPart.TEST_CASE_SPEC: misc_texts.TEST_CASE_SPEC_TITLE,
    HelpPredefinedContentsPart.TEST_SUITE_SPEC: misc_texts.TEST_SUITE_SPEC_TITLE,
}
