import unittest

from exactly_lib.help import cross_reference_id as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(CrossReferenceIdVisitorTest)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class CrossReferenceIdVisitorTest(unittest.TestCase):
    def test_visit_ConceptCrossReferenceId(self):
        # ARRANGE #
        x = sut.ConceptCrossReferenceId('concept name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.ConceptCrossReferenceId],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_EntityCrossReferenceId(self):
        # ARRANGE #
        x = sut.EntityCrossReferenceId('entity type name', 'entity name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.EntityCrossReferenceId],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_ActorCrossReferenceId(self):
        # ARRANGE #
        x = sut.ActorCrossReferenceId('actor name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.ActorCrossReferenceId],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_TestCasePhaseCrossReference(self):
        # ARRANGE #
        x = sut.TestCasePhaseCrossReference('phase name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.TestCasePhaseCrossReference],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_TestCasePhaseInstructionCrossReference(self):
        # ARRANGE #
        x = sut.TestCasePhaseInstructionCrossReference('phase name', 'instruction name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.TestCasePhaseInstructionCrossReference],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_TestSuiteSectionCrossReference(self):
        # ARRANGE #
        x = sut.TestSuiteSectionCrossReference('section name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.TestSuiteSectionCrossReference],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_TestSuiteSectionInstructionCrossReference(self):
        # ARRANGE #
        x = sut.TestSuiteSectionInstructionCrossReference('section name', 'instruction name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.TestSuiteSectionInstructionCrossReference],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_CustomCrossReferenceId(self):
        # ARRANGE #
        x = sut.CustomCrossReferenceId('custom name')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.CustomCrossReferenceId],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_SHOULD_raise_exception_WHEN_an_unknown_class_is_visited(self):
        # ARRANGE #
        x = sut.ProgramCrossReferenceId()
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT & ASSERT#
        with self.assertRaises(TypeError):
            visitor.visit(x)


class VisitorThatRegistersVisitedClassesAndReturnsTheArgument(sut.CrossReferenceIdVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_concept(self, x: sut.ConceptCrossReferenceId):
        self.visited_classes.append(sut.ConceptCrossReferenceId)
        return x

    def visit_entity(self, x: sut.EntityCrossReferenceId):
        self.visited_classes.append(sut.EntityCrossReferenceId)
        return x

    def visit_actor(self, x: sut.ActorCrossReferenceId):
        self.visited_classes.append(sut.ActorCrossReferenceId)
        return x

    def visit_test_case_phase(self, x: sut.TestCasePhaseCrossReference):
        self.visited_classes.append(sut.TestCasePhaseCrossReference)
        return x

    def visit_test_case_phase_instruction(self, x: sut.TestCasePhaseInstructionCrossReference):
        self.visited_classes.append(sut.TestCasePhaseInstructionCrossReference)
        return x

    def visit_test_suite_section(self, x: sut.TestSuiteSectionCrossReference):
        self.visited_classes.append(sut.TestSuiteSectionCrossReference)
        return x

    def visit_test_suite_section_instruction(self, x: sut.TestSuiteSectionInstructionCrossReference):
        self.visited_classes.append(sut.TestSuiteSectionInstructionCrossReference)
        return x

    def visit_custom(self, x: sut.CustomCrossReferenceId):
        self.visited_classes.append(sut.CustomCrossReferenceId)
        return x
