import unittest

from exactly_lib.definitions.cross_ref import concrete_cross_refs as sut
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.util.str_.name import name_with_plural_s
from exactly_lib.util.textformat.structure.core import UrlCrossReferenceTarget, CrossReferenceTarget


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


def entity_type_names(identifier: str,
                      presentation_name: str) -> EntityTypeNames:
    return EntityTypeNames(identifier,
                           name_with_plural_s(presentation_name))


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
        expected = sut.EntityCrossReferenceId(entity_type_names('expected_type_identifier',
                                                                'expected presentation name'),
                                              'expected_entity')
        for actual in ACTUAL_CROSS_REF_ID_OF_EVERY_TYPE:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_not_equals_of_same_type(self):
        # ARRANGE #
        expected_type = 'expected_type'
        expected_presentation_name = 'expected_presentation_name'
        expected_entity = 'expected_entity'
        expected = sut.EntityCrossReferenceId(entity_type_names(expected_type,
                                                                expected_presentation_name),
                                              expected_entity)
        actuals = [
            sut.EntityCrossReferenceId(entity_type_names('actual_type', expected_presentation_name), expected_entity),
            sut.EntityCrossReferenceId(entity_type_names(expected_type, 'actual presentation name'), expected_entity),
            sut.EntityCrossReferenceId(entity_type_names(expected_type, expected_presentation_name), 'actual_entity'),
        ]
        for actual in actuals:
            with self.subTest(actual=actual):
                self.assertNotEqual(expected, actual)

    def test_equals(self):
        # ARRANGE #
        entity_type_name = 'expected_type'
        expected_presentation_name = 'expected_presentation_name'
        entity_name = 'expected_entity'
        expected = sut.EntityCrossReferenceId(entity_type_names(entity_type_name, expected_presentation_name),
                                              entity_name)
        actual = sut.EntityCrossReferenceId(entity_type_names(entity_type_name, expected_presentation_name),
                                            entity_name)
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
    sut.EntityCrossReferenceId(entity_type_names('actual_entity_identifier',
                                                 'actual presentation name'),
                               'actual'),
    sut.TestCasePhaseCrossReference('actual'),
    sut.TestCasePhaseInstructionCrossReference('actual_phase', 'actual_instruction'),
    sut.TestSuiteSectionCrossReference('actual'),
    sut.TestSuiteSectionInstructionCrossReference('actual_section', 'actual_instruction'),
]


class CrossReferenceIdVisitorTest(unittest.TestCase):
    def test_visit_Url(self):
        # ARRANGE #
        x = sut.UrlCrossReferenceTarget('the url')
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.UrlCrossReferenceTarget],
                         visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'The object itself is expected to be returned by the visitor')

    def test_visit_EntityCrossReferenceId(self):
        # ARRANGE #
        x = sut.EntityCrossReferenceId(EntityTypeNames('entity_type_identifier',
                                                       name_with_plural_s('presentation name')),
                                       'entity name')
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

    def test_visit_PredefinedContentsPart(self):
        # ARRANGE #
        x = sut.PredefinedHelpContentsPartReference(sut.HelpPredefinedContentsPart.TEST_SUITE_CLI)
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheArgument()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertEqual([sut.PredefinedHelpContentsPartReference],
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


class VisitorThatRegistersVisitedClassesAndReturnsTheArgument(sut.CrossReferenceTargetVisitor[CrossReferenceTarget]):
    def __init__(self):
        self.visited_classes = []

    def visit_url(self, x: UrlCrossReferenceTarget) -> CrossReferenceTarget:
        self.visited_classes.append(sut.UrlCrossReferenceTarget)
        return x

    def visit_entity(self, x: sut.EntityCrossReferenceId) -> CrossReferenceTarget:
        self.visited_classes.append(sut.EntityCrossReferenceId)
        return x

    def visit_test_case_phase(self, x: sut.TestCasePhaseCrossReference) -> CrossReferenceTarget:
        self.visited_classes.append(sut.TestCasePhaseCrossReference)
        return x

    def visit_test_case_phase_instruction(self, x: sut.TestCasePhaseInstructionCrossReference) -> CrossReferenceTarget:
        self.visited_classes.append(sut.TestCasePhaseInstructionCrossReference)
        return x

    def visit_test_suite_section(self, x: sut.TestSuiteSectionCrossReference) -> CrossReferenceTarget:
        self.visited_classes.append(sut.TestSuiteSectionCrossReference)
        return x

    def visit_test_suite_section_instruction(self,
                                             x: sut.TestSuiteSectionInstructionCrossReference) -> CrossReferenceTarget:
        self.visited_classes.append(sut.TestSuiteSectionInstructionCrossReference)
        return x

    def visit_custom(self, x: sut.CustomCrossReferenceId) -> CrossReferenceTarget:
        self.visited_classes.append(sut.CustomCrossReferenceId)
        return x

    def visit_predefined_part(self, x: sut.PredefinedHelpContentsPartReference) -> CrossReferenceTarget:
        self.visited_classes.append(sut.PredefinedHelpContentsPartReference)
        return x


class UnknownCrossReferenceId(sut.CrossReferenceId):
    pass


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
