import unittest

from exactly_lib.common.help import see_also as sut
from exactly_lib.help_texts.cross_reference_id import CustomCrossReferenceId, TestCasePhaseInstructionCrossReference
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib_test.common.help.test_resources.see_also_assertions import is_see_also_item
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(SeeAlsoItemVisitorTest),
        unittest.makeSuite(TestSeeAlsoUrlInfo),
        unittest.makeSuite(TestSeeAlsoSet),
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


class TestSeeAlsoSet(unittest.TestCase):
    def test_create_empty(self):
        actual = sut.SeeAlsoSet([])
        self.assertEqual(0,
                         len(actual.see_also_items))

    def test_create_non_empty_with_single_element(self):
        element = CustomCrossReferenceId('an_element')
        actual = sut.SeeAlsoSet([element])
        self.assertEqual(1,
                         len(actual.see_also_items))

    def test_create_non_empty_with_duplicate_elements(self):
        element = CustomCrossReferenceId('an_element')
        actual = sut.SeeAlsoSet([element, element])
        self.assertEqual(1,
                         len(actual.see_also_items))

    def test_union(self):
        cases = [
            (
                'both sets are empty',
                sut.SeeAlsoSet([]),
                sut.SeeAlsoSet([]),
                0,
            ),
            (
                'one empty and one non-empty',
                sut.SeeAlsoSet([CustomCrossReferenceId('an_element')]),
                sut.SeeAlsoSet([]),
                1,
            ),
            (
                'two non-empty with different elements',
                sut.SeeAlsoSet([CustomCrossReferenceId('a')]),
                sut.SeeAlsoSet([CustomCrossReferenceId('b')]),
                2,
            ),
            (
                'two non-empty with equal elements',
                sut.SeeAlsoSet([CustomCrossReferenceId('a')]),
                sut.SeeAlsoSet([CustomCrossReferenceId('a')]),
                1,
            ),

        ]
        for name, a, b, expected_size in cases:
            with self.subTest(name=name):
                actual = a.union(b)
                self.assertEqual(expected_size, len(actual.see_also_items))

    def test_elements_SHOULD_be_translated_to_see_also_items(self):
        cases = [
            NameAndValue('empty',
                         (sut.SeeAlsoSet([]),
                          asrt.matches_sequence([])
                          )),
            NameAndValue('single cross ref',
                         (sut.SeeAlsoSet([CustomCrossReferenceId('target')]),
                          asrt.matches_sequence([is_see_also_item])
                          )),
            NameAndValue('single see also url info',
                         (sut.SeeAlsoSet([sut.SeeAlsoUrlInfo('name', 'url')]),
                          asrt.matches_sequence([is_see_also_item])
                          )),
            NameAndValue(' see also url info and cross ref',
                         (sut.SeeAlsoSet([sut.SeeAlsoUrlInfo('name', 'url'),
                                          TestCasePhaseInstructionCrossReference('phase', 'instruction')]),
                          asrt.matches_sequence([is_see_also_item,
                                                 is_see_also_item])
                          )),
        ]
        for case in cases:
            see_also_set, assertion = case.value
            with self.subTest(name=case.name):
                # ACT #
                actual = see_also_set.see_also_items
                # ASSERT #
                assertion.apply_without_message(self, actual)
