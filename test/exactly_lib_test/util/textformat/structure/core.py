import unittest

from exactly_lib.util.textformat.structure import core as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestAccept)


class TestAccept(unittest.TestCase):
    def test_cross_reference(self):
        # ARRANGE #
        item = sut.CrossReferenceText(sut.StringText('cross ref title'),
                                      sut.CrossReferenceTarget())
        visitor = AVisitorThatRecordsClassForMethod()
        # ACT #
        ret_val = item.accept(visitor)
        # ASSERT #
        self.assertIs(ret_val, item)
        self.assertEqual(1, len(visitor.visited_class),
                         'number of methods')
        self.assertIs(sut.CrossReferenceText,
                      visitor.visited_class[0],
                      'method')

    def test_anchor(self):
        # ARRANGE #
        item = sut.AnchorText(sut.StringText('concrete string text'),
                              sut.CrossReferenceTarget())
        visitor = AVisitorThatRecordsClassForMethod()
        # ACT #
        ret_val = item.accept(visitor)
        # ASSERT #
        self.assertIs(ret_val, item)
        self.assertEqual(1, len(visitor.visited_class),
                         'number of methods')
        self.assertIs(sut.AnchorText,
                      visitor.visited_class[0],
                      'method')

    def test_visit_string(self):
        # ARRANGE #
        item = sut.StringText('string text')
        visitor = AVisitorThatRecordsClassForMethod()
        # ACT #
        ret_val = item.accept(visitor)
        # ASSERT #
        self.assertIs(ret_val, item)
        self.assertEqual(1, len(visitor.visited_class),
                         'number of methods')
        self.assertIs(sut.StringText,
                      visitor.visited_class[0],
                      'method')


class AVisitorThatRecordsClassForMethod(sut.TextVisitor[sut.Text]):
    def __init__(self):
        self.visited_class = []

    def visit_cross_reference(self, text: sut.CrossReferenceText) -> sut.Text:
        self.visited_class.append(sut.CrossReferenceText)
        return text

    def visit_anchor(self, text: sut.AnchorText) -> sut.Text:
        self.visited_class.append(sut.AnchorText)
        return text

    def visit_string(self, text: sut.StringText) -> sut.Text:
        self.visited_class.append(sut.StringText)
        return text


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
