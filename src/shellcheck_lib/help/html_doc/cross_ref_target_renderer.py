from shellcheck_lib.help import cross_reference_id as cross_ref
from shellcheck_lib.util.textformat.formatting.html import text
from shellcheck_lib.util.textformat.structure import core as doc


class HtmlTargetRenderer(text.TargetRenderer, cross_ref.CrossReferenceIdVisitor):
    def apply(self, target: doc.CrossReferenceTarget) -> str:
        return self.visit(target)

    def visit_concept(self, x: cross_ref.ConceptCrossReferenceId):
        return 'concept.' + x.concept_name

    def visit_test_case_phase(self, x: cross_ref.TestCasePhaseCrossReference):
        return 'test-case-phase.' + x.phase_name

    def visit_test_case_phase_instruction(self, x: cross_ref.TestCasePhaseInstructionCrossReference):
        return 'test-case-instruction.%s.%s' % (x.phase_name, x.instruction_name)

    def visit_custom(self, x: cross_ref.CustomCrossReferenceId):
        return 'custom.' + x.target_name
