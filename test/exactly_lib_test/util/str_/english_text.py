import unittest

from exactly_lib.util.str_ import english_text as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestOrSequence(),
    ])


class TestOrSequence(unittest.TestCase):
    def runTest(self):
        cases = [
            (
                [],
                ''
            ),
            (
                ['a'],
                'a'
            ),
            (
                ['a'],
                'a'
            ),
            (
                ['a', 'b'],
                'a or b'
            ),
            (
                ['a', 'b', 'c'],
                'a, b or c'
            ),
            (
                ['a', 'b', 'c', 'd'],
                'a, b, c or d'
            ),
        ]
        for case in cases:
            with self.subTest(case[0]):
                # ACT #
                actual = sut.or_sequence(case[0])
                # ASSERT #
                self.assertEqual(case[1],
                                 actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
