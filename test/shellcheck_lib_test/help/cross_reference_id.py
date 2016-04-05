import unittest

from shellcheck_lib.help import cross_reference_id as sut


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

    def visit_custom(self, x: sut.CustomCrossReferenceId):
        self.visited_classes.append(sut.CustomCrossReferenceId)
        return x
