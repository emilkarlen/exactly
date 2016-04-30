from exactly_lib.help import cross_reference_id
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.util.textformat.structure.core import Text, CrossReferenceText


class CrossReferenceTextConstructor(object):
    def apply(self, x: cross_reference_id.CrossReferenceId) -> Text:
        return CrossReferenceText(_TITLE_RENDERER.visit(x),
                                  x)


class _TitleRenderer(cross_reference_id.CrossReferenceIdVisitor):
    def __init__(self):
        self.any_instruction = AnyInstructionNameDictionary()
        self.phase_name_dict = phase_name_dictionary()

    def visit_custom(self, x: cross_reference_id.CustomCrossReferenceId):
        raise ValueError('Rendering of custom cross references is not supported ("%s")' %
                         x.target_name)

    def visit_test_case_phase(self, x: cross_reference_id.TestCasePhaseCrossReference):
        return 'Phase %s' % self.phase_name_dict[x.phase_name]

    def visit_test_case_phase_instruction(self, x: cross_reference_id.TestCasePhaseInstructionCrossReference):
        return 'Instruction "{i}" (in phase {p})'.format(i=self.any_instruction[x.instruction_name],
                                                         p=self.phase_name_dict[x.phase_name])

    def visit_concept(self, x: cross_reference_id.ConceptCrossReferenceId):
        return 'Concept "' + x.concept_name + '"'


_TITLE_RENDERER = _TitleRenderer()
