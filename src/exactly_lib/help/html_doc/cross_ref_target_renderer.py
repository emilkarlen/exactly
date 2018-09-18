from exactly_lib.definitions.cross_ref import concrete_cross_refs as cross_ref
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference
from exactly_lib.util.textformat.rendering.html.cross_ref import TargetRenderer
from exactly_lib.util.textformat.structure import core as doc
from exactly_lib.util.textformat.structure.core import UrlCrossReferenceTarget


class HtmlTargetRenderer(TargetRenderer, cross_ref.CrossReferenceIdVisitor):
    def apply(self, target: doc.CrossReferenceTarget) -> str:
        return self.visit(target)

    def visit_entity(self, x: cross_ref.EntityCrossReferenceId):
        return 'entity' + '.' + x.entity_type_identifier + '.' + x.entity_name.replace(' ', '-')

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

    def visit_url(self, x: UrlCrossReferenceTarget):
        return x.url

    def visit_predefined_part(self, x: PredefinedHelpContentsPartReference):
        return 'help-part.' + x.part.name
