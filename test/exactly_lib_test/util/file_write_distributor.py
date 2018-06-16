import io
import unittest

from exactly_lib.util import file_write_distributor as sut


def suite() -> unittest.TestCase:
    return unittest.makeSuite(TestFileWriteDistributor)


class TestFileWriteDistributor(unittest.TestCase):
    def test_no_files(self):
        # ARRANGE #

        fwd = sut.FileWriteDistributor([])

        # ACT #

        num_chars_written = fwd.write('hello')

        # ASSERT #

        self.assertEqual(0, num_chars_written)

    def test_single_file(self):
        # ARRANGE #

        f = io.StringIO()
        fwd = sut.FileWriteDistributor([f])

        string_1 = 'hello'
        string_2 = ' world'

        # ACT #

        num_chars_written_1 = fwd.write(string_1)
        num_chars_written_2 = fwd.write(string_2)

        # ASSERT #

        self.assertEqual(string_1 + string_2,
                         f.getvalue(),
                         'written string')

        self.assertEqual(len(string_1) + len(string_2),
                         num_chars_written_1 + num_chars_written_2,
                         'number of chars written')

    def test_write_SHOULD_be_distributed_to_evey_file(self):
        # ARRANGE #

        f1 = io.StringIO()
        f2 = io.StringIO()
        fwd = sut.FileWriteDistributor([f1, f2])

        string_1 = 'hello'
        string_2 = ' world'

        # ACT #

        num_chars_written_1 = fwd.write(string_1)
        num_chars_written_2 = fwd.write(string_2)

        # ASSERT #

        self.assertEqual(string_1 + string_2,
                         f1.getvalue(),
                         'written string to file 1')

        self.assertEqual(string_1 + string_2,
                         f2.getvalue(),
                         'written string to file 2')

        self.assertEqual(len(string_1) + len(string_2),
                         num_chars_written_1 + num_chars_written_2,
                         'number of chars written')

    def test_return_value_SHOULD_be_return_value_from_first_file(self):
        # ARRANGE #

        f1 = io.StringIO()
        f2 = NadaWriter()

        fwd = sut.FileWriteDistributor([f1, f2])

        string = 'hello, world'

        # ACT #

        num_chars_written = fwd.write(string)

        # ASSERT #

        self.assertEqual(len(string),
                         num_chars_written,
                         'number of chars written')


class NadaWriter:
    """Writer that returns constant 0"""

    def write(self, s: str) -> int:
        return 0
