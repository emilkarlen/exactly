import unittest

from exactly_lib.util import tables as sut


class TestExtendLengths(unittest.TestCase):
    def test_single_row(self):
        # ARRANGE #
        single_row_table = [[1, 2]]
        # ACT #
        actual = sut.extend_each_sub_list_to_max_sub_list_length(single_row_table, 'fill')
        # ASSERT #
        expected = [[1, 2]]
        self.assertEqual(expected,
                         actual)

    def test_multiple_rows(self):
        # ARRANGE #
        single_row_table = [[1, 2],
                            [1],
                            [],
                            [1, 2, 3]]
        # ACT #
        actual = sut.extend_each_sub_list_to_max_sub_list_length(single_row_table, 'fill')
        # ASSERT #
        expected = [[1, 2, 'fill'],
                    [1, 'fill', 'fill'],
                    ['fill', 'fill', 'fill'],
                    [1, 2, 3]
                    ]
        self.assertEqual(expected,
                         actual)


class TestTranspose(unittest.TestCase):
    def test_empty(self):
        self.assertEqual([],
                         sut.transpose([]))

    def test_single_row(self):
        # ARRANGE #
        single_row_table = [['a', 'b']]
        # ACT #
        actual = sut.transpose(single_row_table)
        # ASSERT #
        expected = [['a'],
                    ['b']]
        self.assertEqual(expected,
                         actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTranspose),
        unittest.makeSuite(TestExtendLengths),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
