import unittest

from exactly_lib.common.err_msg import utils as sut
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPrefixFirstBlock)


class TestPrefixFirstBlock(unittest.TestCase):
    def test(self):
        # ARRANGE #
        non_empty_block_1 = ['part of non-empty block 1']
        non_empty_block_2 = ['part of non-empty block 2']
        cases = [
            NIE('everything is empty',
                input_value=([], []),
                expected_value=[],
                ),
            NIE('prefix is empty',
                input_value=([], [non_empty_block_1]),
                expected_value=[non_empty_block_1],
                ),
            NIE('blocks is empty',
                input_value=(non_empty_block_1, []),
                expected_value=[non_empty_block_1],
                ),
            NIE('none is empty',
                input_value=(non_empty_block_1, [non_empty_block_2]),
                expected_value=[non_empty_block_1 + non_empty_block_2],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = sut.prefix_first_block(*case.input_value)
                # ASSERT #
                self.assertEqual(case.expected_value,
                                 actual)
