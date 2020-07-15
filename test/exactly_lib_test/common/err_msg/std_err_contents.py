import io
import unittest

from exactly_lib.common.err_msg import std_err_contents as sut
from exactly_lib_test.test_resources.test_utils import NIE


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInitialPartReaderWithRestIndicator(),
    ])


class TestInitialPartReaderWithRestIndicator(unittest.TestCase):
    def runTest(self):
        max_num_lines = 2
        max_num_chars = 10
        reader = sut.InitialPartReaderWithRestIndicator(max_num_lines, max_num_chars)
        cases = [
            NIE(
                'read all, single line',
                input_value='x' * (max_num_chars - 1),
                expected_value='x' * (max_num_chars - 1),
            ),
            NIE(
                'read all, multiple lines',
                input_value='1\n2\n',
                expected_value='1\n2\n',
            ),
            NIE(
                'read limited (num chars), single line',
                input_value='x' * (max_num_chars + 1),
                expected_value=('x' * max_num_chars) + sut.InitialPartReaderWithRestIndicator.REST_INDICATOR,
            ),
            NIE(
                'read limited (num chars), multiple lines',
                input_value='1234567\n1234567\n',
                expected_value='1234567\n12' + sut.InitialPartReaderWithRestIndicator.REST_INDICATOR,
            ),
            NIE(
                'read limited (num lines)',
                input_value='1\n2\n3\n',
                expected_value='1\n2\n' + sut.InitialPartReaderWithRestIndicator.REST_INDICATOR,
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                input_file = io.StringIO(case.input_value)
                # ACT #
                actual = reader.read(input_file)
                # ASSERT #
                self.assertEqual(case.expected_value, actual)
