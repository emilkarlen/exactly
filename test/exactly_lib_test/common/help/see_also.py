import unittest

from exactly_lib.common.help import see_also as sut
from exactly_lib.help_texts.cross_reference_id import CustomCrossReferenceId
from exactly_lib.util.textformat.structure.core import StringText


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(SeeAlsoItemVisitorTest),
        unittest.makeSuite(TestSeeAlsoUrlInfo),
        unittest.makeSuite(TestCrossReferenceSet),
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


class TestCrossReferenceSet(unittest.TestCase):
    def test_create_empty(self):
        actual = sut.CrossReferenceIdSet([])
        self.assertEqual(0,
                         len(actual.cross_references))

    def test_create_non_empty(self):
        cross_ref = CustomCrossReferenceId('target_name')
        actual = sut.CrossReferenceIdSet([cross_ref])
        self.assertEqual((cross_ref,),
                         actual.cross_references)

    def test_union(self):
        cases = [
            (
                'both sets are empty',
                sut.CrossReferenceIdSet([]),
                sut.CrossReferenceIdSet([]),
                [],
            ),
            (
                'one empty and one non-empty',
                sut.CrossReferenceIdSet([CustomCrossReferenceId('target_name')]),
                sut.CrossReferenceIdSet([]),
                [CustomCrossReferenceId('target_name')],
            ),
            (
                'two non-empty with different elements',
                sut.CrossReferenceIdSet([CustomCrossReferenceId('a')]),
                sut.CrossReferenceIdSet([CustomCrossReferenceId('b')]),
                [CustomCrossReferenceId('a'),
                 CustomCrossReferenceId('b')],
            ),
            (
                'two non-empty with equal elements',
                sut.CrossReferenceIdSet([CustomCrossReferenceId('a')]),
                sut.CrossReferenceIdSet([CustomCrossReferenceId('a')]),
                [CustomCrossReferenceId('a')],
            ),

        ]
        for name, a, b, expected in cases:
            with self.subTest(name=name,
                              order='left to right'):
                actual = a.union(b)
                self._assert_equals_module_order(actual.cross_references, expected)
            with self.subTest(name=name,
                              order='right to left'):
                actual = b.union(a)
                self._assert_equals_module_order(actual.cross_references, expected)

    def _assert_equals_module_order(self,
                                    actual: sut.CrossReferenceIdSet,
                                    expected: sut.CrossReferenceIdSet):
        self.assertEqual(len(expected),
                         len(actual),
                         'number of elements')
        for a in actual:
            self.assertIn(a, expected)
