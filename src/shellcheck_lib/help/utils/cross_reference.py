from shellcheck_lib.help import cross_reference_id
from shellcheck_lib.util.textformat.structure.core import Text, CrossReferenceText


class CrossReferenceTextConstructor(object):
    def apply(self, x: cross_reference_id.CrossReferenceId) -> Text:
        return CrossReferenceText(_TITLE_RENDERER.visit(x),
                                  x)


class _TitleRenderer(cross_reference_id.CrossReferenceIdVisitor):
    def visit_custom(self, x: cross_reference_id.CustomCrossReferenceId):
        return 'TODO should this be removed?'

    def visit_test_case_phase(self, x: cross_reference_id.TestCasePhaseCrossReference):
        return 'TODO is this correct? "%s"' % x.phase_name

    def visit_test_case_phase_instruction(self, x: cross_reference_id.TestCasePhaseInstructionCrossReference):
        return 'TODO phase/instr %s/%s' % (x.phase_name, x.instruction_name)

    def visit_concept(self, x: cross_reference_id.ConceptCrossReferenceId):
        return 'Concept "' + x.concept_name + '"'


_TITLE_RENDERER = _TitleRenderer()
