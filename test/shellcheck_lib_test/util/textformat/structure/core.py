import unittest

from exactly_lib.util.textformat.structure import core as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestTextVisitor)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestTextVisitor(unittest.TestCase):
    def test_visit_cross_reference(self):
        # ARRANGE #
        item = sut.CrossReferenceText('cross ref title', sut.CrossReferenceTarget())
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([sut.CrossReferenceText],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_anchor(self):
        # ARRANGE #
        item = sut.AnchorText(sut.CrossReferenceTarget(),
                              sut.StringText('concrete string text'))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([sut.AnchorText],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_string(self):
        # ARRANGE #
        item = sut.StringText('string text')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([sut.StringText],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_unknown_object(self):
        # ARRANGE #
        item = 'A value of a type that is not a Text'
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(ValueError):
            visitor.visit(item)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.TextVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_cross_reference(self, text: sut.CrossReferenceText):
        self.visited_types.append(sut.CrossReferenceText)
        return text

    def visit_anchor(self, text: sut.AnchorText):
        self.visited_types.append(sut.AnchorText)
        return text

    def visit_string(self, text: sut.StringText):
        self.visited_types.append(sut.StringText)
        return text
