import unittest

from exactly_lib.util import collection as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFrozenSetBasedOnEquality)


class TestFrozenSetBasedOnEquality(unittest.TestCase):
    def test_create_empty(self):
        actual = sut.FrozenSetBasedOnEquality([])
        self.assertEqual(0,
                         len(actual.elements))

    def test_create_non_empty_with_single_element(self):
        element = 'an_element'
        actual = sut.FrozenSetBasedOnEquality([element])
        self.assertEqual((element,),
                         actual.elements)

    def test_create_non_empty_with_duplicate_elements(self):
        element = 'an_element'
        actual = sut.FrozenSetBasedOnEquality([element, element])
        self.assertEqual((element,),
                         actual.elements)

    def test_union(self):
        cases = [
            (
                'both sets are empty',
                sut.FrozenSetBasedOnEquality([]),
                sut.FrozenSetBasedOnEquality([]),
                [],
            ),
            (
                'one empty and one non-empty',
                sut.FrozenSetBasedOnEquality(['an_element']),
                sut.FrozenSetBasedOnEquality([]),
                ['an_element'],
            ),
            (
                'two non-empty with different elements',
                sut.FrozenSetBasedOnEquality(['a']),
                sut.FrozenSetBasedOnEquality(['b']),
                ['a',
                 'b'],
            ),
            (
                'two non-empty with equal elements',
                sut.FrozenSetBasedOnEquality(['a']),
                sut.FrozenSetBasedOnEquality(['a']),
                ['a'],
            ),

        ]
        for name, a, b, expected in cases:
            with self.subTest(name=name,
                              order='left to right'):
                actual = a.union(b)
                self._assert_equals_module_order(actual.elements, expected)
            with self.subTest(name=name,
                              order='right to left'):
                actual = b.union(a)
                self._assert_equals_module_order(actual.elements, expected)

    def _assert_equals_module_order(self,
                                    actual: sut.FrozenSetBasedOnEquality,
                                    expected: sut.FrozenSetBasedOnEquality):
        self.assertEqual(len(expected),
                         len(actual),
                         'number of elements')
        for a in actual:
            self.assertIn(a, expected)
