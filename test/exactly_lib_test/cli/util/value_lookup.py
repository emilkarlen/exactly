import unittest

from exactly_lib.cli.util import value_lookup as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatch),
        unittest.makeSuite(TestNoMatch),
        unittest.makeSuite(TestMultipleMatches),
    ])


class TestMatch(unittest.TestCase):
    def test_WHEN_sequence_contains_exactly_key_pattern_THEN_corresponding_value_SHOULD_be_returned(self):
        cases = [('1', 1, [('1', 1)]),
                 ('2', 2, [('1', 1), ('2', 2)])]
        for key_pattern, expected_value, iterable in cases:
            with self.subTest(key_pattern=key_pattern, expected_value=expected_value, iterable=iterable):
                actual = sut.lookup(key_pattern, iterable)
                self._assertIsExactMatch(key_pattern, expected_value, actual)

    def test_WHEN_sequence_contains_key_pattern_as_sub_string_THEN_corresponding_value_SHOULD_be_returned(self):
        cases = [('b', 'abc', 1, [('abc', 1)]),
                 ('ab', 'abc', 2, [('ac', 1), ('abc', 2)])]
        for key_pattern, expected_key, expected_value, iterable in cases:
            with self.subTest(key_pattern=key_pattern,
                              expected_key=expected_key, expected_value=expected_value,
                              iterable=iterable):
                actual = sut.lookup(key_pattern, iterable)
                self._assertIsInexactMatch(expected_key, expected_value, actual)

    def test_exact_match_should_have_precedence_over_sub_string_match(self):
        # ARRANGE #
        iterable = [('snake skin', 1),
                    ('rattle snake', 2),
                    ('snake', 3)
                    ]
        key_pattern = 'snake'
        # ACT #
        actual = sut.lookup(key_pattern, iterable)
        # ASSERT #
        self._assertIsExactMatch('snake', 3, actual)

    def test_iterable_should_not_need_to_be_a_list(self):
        # ARRANGE #
        iterable = iter([('1', 1)])
        key_pattern = '1'
        # ACT #
        actual = sut.lookup(key_pattern, iterable)
        # ASSERT #
        self._assertIsExactMatch('1', 1, actual)

    def _assertIsExactMatch(self, key: str, value, actual: sut.Match):
        self._assertEqual(_exact_match(key, value), actual)

    def _assertIsInexactMatch(self, key: str, value, actual: sut.Match):
        self._assertEqual(_inexact_match(key, value), actual)

    def _assertEqual(self, expected: sut.Match, actual: sut.Match):
        self.assertEqual(expected.value, actual.value, 'value')
        self.assertEqual(expected.key, actual.key, 'key')
        self.assertEqual(expected.is_exact_match, actual.is_exact_match, 'is_exact_match')


class TestNoMatch(unittest.TestCase):
    def test_WHEN_sequence_is_empty_THEN_NoMatchError_SHOULD_be_raised(self):
        with self.assertRaises(sut.NoMatchError):
            sut.lookup('key', [])

    def test_WHEN_no_key_contains_key_pattern_THEN_NoMatchError_SHOULD_be_raised(self):
        with self.assertRaises(sut.NoMatchError):
            sut.lookup('key', [('1', 1), ('2', 2)])


class TestMultipleMatches(unittest.TestCase):
    def test_WHEN_sequence_is_empty_THEN_NoMatchError_SHOULD_be_raised(self):
        with self.assertRaises(sut.MultipleMatchesError) as cm:
            # ARRANGE #
            iterable = iter([('aB', 1),
                             ('Bc', 2),
                             ('no match', 3)])
            key_pattern = 'B'
            # ACT #
            actual = sut.lookup(key_pattern, iterable)
            # ASSERT #
            expected_matches = [('aB', 1),
                                ('Bc', 2)]
            self.assertListEqual(expected_matches, cm.ex.matching_key_values)


def _exact_match(key, value) -> sut.Match:
    return sut.Match(key, value, True)


def _inexact_match(key, value) -> sut.Match:
    return sut.Match(key, value, False)
