from exactly_lib.help import cross_reference_id
from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.phase_names import phase_name_dictionary, phase_name_dict_key_for
from exactly_lib.help.utils.suite_section_names import suite_section_name_dictionary, suite_section_name_dict_key_for
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText


class CrossReferenceTextConstructor(object):
    def apply(self, x: cross_reference_id.CrossReferenceId) -> Text:
        return CrossReferenceText(_TITLE_RENDERER.visit(x),
                                  x)


class _TitleRenderer(cross_reference_id.CrossReferenceIdVisitor):
    def __init__(self):
        self.any_instruction = AnyInstructionNameDictionary()
        self.phase_name_dict = phase_name_dictionary()
        self.suite_section_name_dict = suite_section_name_dictionary()

    def visit_custom(self, x: cross_reference_id.CustomCrossReferenceId):
        raise ValueError('Rendering of custom cross references is not supported ("%s")' %
                         x.target_name)

    def visit_test_case_phase(self, x: cross_reference_id.TestCasePhaseCrossReference):
        return 'Phase %s' % self.phase_name_dict[phase_name_dict_key_for(x.phase_name)].syntax

    def visit_test_case_phase_instruction(self, x: cross_reference_id.TestCasePhaseInstructionCrossReference):
        return 'Instruction {i} (in phase {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=self.phase_name_dict[phase_name_dict_key_for(x.phase_name)].syntax)

    def visit_test_suite_section(self, x: cross_reference_id.TestSuiteSectionCrossReference):
        return 'Suite section %s' % self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax

    def visit_test_suite_section_instruction(self, x: cross_reference_id.TestSuiteSectionInstructionCrossReference):
        return 'Suite instruction {i} (in section {p})'.format(
            i=self.any_instruction[x.instruction_name],
            p=self.suite_section_name_dict[suite_section_name_dict_key_for(x.section_name)].syntax)

    def visit_entity(self, x: EntityCrossReferenceId):
        return x.entity_type_name.capitalize() + ' "' + x.entity_name + '"'


_TITLE_RENDERER = _TitleRenderer()
