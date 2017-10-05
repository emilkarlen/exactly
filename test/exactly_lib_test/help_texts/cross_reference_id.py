import unittest

from exactly_lib.help_texts import cross_reference_id as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsCustom),
        unittest.makeSuite(TestEqualsEntity),
        unittest.makeSuite(TestEqualsTestCasePhase),
        unittest.makeSuite(TestEqualsTestCasePhaseInstruction),
        unittest.makeSuite(TestEqualsTestCaseSection),
        unittest.makeSuite(TestEqualsTestSuiteSectionInstruction),

        unittest.makeSuite(CrossReferenceIdVisitorTest),
    ])


class TestEqualsCustom(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.CustomCrossReferenceId('expected')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        target_name = 'expected'
        expected = sut.CustomCrossReferenceId(target_name)
        actual = sut.CustomCrossReferenceId(target_name)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestEqualsEntity(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.EntityCrossReferenceId('expected_type', 'expected_entity')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_not_equals_of_same_type(self):
        # ARRANGE #
        expected_type = 'expected_type'
        expected_entity = 'expected_entity'
        expected = sut.EntityCrossReferenceId(expected_type, expected_entity)
        actuals = [
            sut.EntityCrossReferenceId('actual_type', expected_entity),
            sut.EntityCrossReferenceId(expected_type, 'actual_entity'),
        ]
        for actual in actuals:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        target_name = 'expected'
        entity_type_name = 'expected_type'
        entity_name = 'expected_entity'
        expected = sut.EntityCrossReferenceId(entity_type_name, entity_name)
        actual = sut.EntityCrossReferenceId(entity_type_name, entity_name)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestEqualsTestCasePhase(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.TestCasePhaseCrossReference('expected_phase')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        phase_name = 'expected_phase'
        expected = sut.TestCasePhaseCrossReference(phase_name)
        actual = sut.TestCasePhaseCrossReference(phase_name)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestEqualsTestCasePhaseInstruction(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.TestCasePhaseInstructionCrossReference('expected_phase', 'expected_instruction')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_not_equals_of_same_type(self):
        # ARRANGE #
        expected_phase = 'expected_phase'
        expected_instruction = 'expected_instruction'
        expected = sut.TestCasePhaseInstructionCrossReference(expected_phase, expected_instruction)
        actuals = [
            sut.TestCasePhaseInstructionCrossReference('actual_phase', expected_instruction),
            sut.TestCasePhaseInstructionCrossReference(expected_phase, 'actual_instruction'),
        ]
        for actual in actuals:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        phase_name = 'expected_phase'
        instruction_name = 'expected_instruction'
        expected = sut.TestCasePhaseInstructionCrossReference(phase_name, instruction_name)
        actual = sut.TestCasePhaseInstructionCrossReference(phase_name, instruction_name)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestEqualsTestCaseSection(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.TestSuiteSectionCrossReference('expected_section')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        section_name = 'expected_section'
        expected = sut.TestSuiteSectionCrossReference(section_name)
        actual = sut.TestSuiteSectionCrossReference(section_name)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestEqualsTestSuiteSectionInstruction(unittest.TestCase):
    def test_not_equals_for_every_type(self):
        expected = sut.TestSuiteSectionInstructionCrossReference('expected_section', 'expected_instruction')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_not_equals_of_same_type(self):
        # ARRANGE #
        expected_section = 'expected_section'
        expected_instruction = 'expected_instruction'
        expected = sut.TestSuiteSectionInstructionCrossReference(expected_section, expected_instruction)
        actuals = [
            sut.TestSuiteSectionInstructionCrossReference('actual_section', expected_instruction),
            sut.TestSuiteSectionInstructionCrossReference(expected_section, 'actual_instruction'),
        ]
        for actual in actuals:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        section_name = 'expected_section'
        instruction_name = 'expected_instruction'
        expected = sut.TestSuiteSectionInstructionCrossReference(section_name, instruction_name)
        actual = sut.TestSuiteSectionInstructionCrossReference(section_name, instruction_name)
        # ASSERT #
        self.assertEqual(expected, actual)


ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE = [
    sut.CustomCrossReferenceId('actual'),
    sut.EntityCrossReferenceId('actual_entity', 'actual'),
    sut.TestCasePhaseCrossReference('actual'),
    sut.TestCasePhaseInstructionCrossReference('actual_phase', 'actual_instruction'),
    sut.TestSuiteSectionCrossReference('actual'),
    sut.TestSuiteSectionInstructionCrossReference('actual_section', 'actual_instruction'),
]


class CrossReferenceIdVisitorTest(unittest.TestCase):
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
        x = UnknownCrossReferenceId()
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT & ASSERT#
        with self.assertRaises(TypeError):
            visitor.visit(x)


class VisitorThatRegistersVisitedClassesAndReturnsTheArgument(sut.CrossReferenceIdVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_entity(self, x: sut.EntityCrossReferenceId):
        self.visited_classes.append(sut.EntityCrossReferenceId)
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


class UnknownCrossReferenceId(sut.CrossReferenceId):
    pass


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
