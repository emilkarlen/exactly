from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.util.textformat.formatting.html import text
from exactly_lib.util.textformat.structure import core as doc


class HtmlTargetRenderer(text.TargetRenderer, cross_ref.CrossReferenceIdVisitor):
    def apply(self, target: doc.CrossReferenceTarget) -> str:
        return self.visit(target)

    def visit_entity(self, x: EntityCrossReferenceId):
        return 'entity' + '.' + x.entity_type_name + '.' + x.entity_name

    def visit_concept(self, x: cross_ref.ConceptCrossReferenceId):
        return 'concept.' + x.concept_name

    def visit_test_case_phase(self, x: cross_ref.TestCasePhaseCrossReference):
        return 'test-case.phase.' + x.phase_name

    def visit_test_case_phase_instruction(self, x: cross_ref.TestCasePhaseInstructionCrossReference):
        return 'test-case.instruction.%s.%s' % (x.phase_name, x.instruction_name)

    def visit_test_suite_section(self, x: cross_ref.TestSuiteSectionCrossReference):
        return 'test-suite.section.' + x.section_name

    def visit_test_suite_section_instruction(self, x: cross_ref.TestSuiteSectionInstructionCrossReference):
        return 'test-suite.instruction.%s.%s' % (x.section_name, x.instruction_name)

    def visit_custom(self, x: cross_ref.CustomCrossReferenceId):
        return 'custom.' + x.target_name
