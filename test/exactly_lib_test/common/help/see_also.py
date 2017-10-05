import unittest

from exactly_lib.common.help import see_also as sut
from exactly_lib.help_texts.cross_reference_id import CustomCrossReferenceId
from exactly_lib.util.textformat.structure.core import StringText


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(SeeAlsoItemVisitorTest),
        unittest.makeSuite(TestSeeAlsoUrlInfo),
    ])


class SeeAlsoItemVisitorTest(unittest.TestCase):
    def test_cross_reference_id(self):
        self._check(sut.CrossReferenceIdSeeAlsoItem(CustomCrossReferenceId('target name')),
                    sut.CrossReferenceIdSeeAlsoItem)

    def test_text(self):
        self._check(sut.TextSeeAlsoItem(StringText('text value')),
                    sut.TextSeeAlsoItem)

    def test_visit_SHOULD_raise_TypeError_WHEN_argument_is_not_a_sub_class_of_argument(self):
        visitor = ArgumentRecordingVisitor()
        with self.assertRaises(TypeError):
            visitor.visit('not an argument usage')

    def _check(self, x: sut.SeeAlsoItem, expected_class):
        # ARRANGE #
        visitor = ArgumentRecordingVisitor()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertListEqual([expected_class],
                             visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'Visitor should return the return-value of the visited method')


class ArgumentRecordingVisitor(sut.SeeAlsoItemVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_cross_reference_id(self, x: sut.CrossReferenceIdSeeAlsoItem):
        self.visited_classes.append(sut.CrossReferenceIdSeeAlsoItem)
        return x

    def visit_text(self, x: sut.TextSeeAlsoItem):
        self.visited_classes.append(sut.TextSeeAlsoItem)
        return x


class TestSeeAlsoUrlInfo(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        title = 'the title'
        url = 'the url'
        expected = sut.SeeAlsoUrlInfo(title, url)
        actual = sut.SeeAlsoUrlInfo(title, url)
        # ASSERT #
        self.assertEqual(expected, actual)

    def test_not_equals(self):
        # ARRANGE #
        expected_title = 'expected title'
        expected_url = 'expected url'
        expected = sut.SeeAlsoUrlInfo(expected_title, expected_url)
        actuals = [
            sut.SeeAlsoUrlInfo('actual title', expected_url),
            sut.SeeAlsoUrlInfo(expected_title, 'actual url')
        ]
        for actual in actuals:
            with self.subTest(actual=actual):
                # ASSERT #
                self.assertNotEqual(expected, actual)
