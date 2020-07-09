import itertools
import unittest

from exactly_lib.util.str_ import sequences as sut
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(IntStringsTest),
    ])


class Conf:
    def __init__(self,
                 start: int,
                 width: int,
                 num_items_to_take: int,
                 ):
        self.start = start
        self.width = width
        self.num_items_to_take = num_items_to_take


class IntStringsTest(unittest.TestCase):
    def runTest(self):
        cases = [
            NIE(
                'start=1, width=0',
                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                Conf(start=1, width=0, num_items_to_take=11),
            ),
            NIE(
                'start=1, width=1',
                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                Conf(start=1, width=1, num_items_to_take=11),
            ),
            NIE(
                'start=0, width=2',
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11'],
                Conf(start=0, width=2, num_items_to_take=12),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                conf = case.input_value
                # ACT #
                actual = sut.int_strings(conf.start, conf.width)
                # ASSERT #
                actual_to_take = list(itertools.islice(actual, conf.num_items_to_take))
                self.assertEqual(case.expected_value,
                                 actual_to_take)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
