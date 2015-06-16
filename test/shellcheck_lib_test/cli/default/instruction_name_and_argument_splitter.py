import unittest

from shellcheck_lib.cli.default.instruction_name_and_argument_splitter import splitter


class TestCase(unittest.TestCase):
    def test_single_character_name_and_no_argument(self):
        self._check('i', 'i', '')

    def _check(self,
               line: str,
               expected_name: str,
               expected_argument: str):
        # ACT #
        (actual_name, actual_arg) = splitter(line)
        # ASSERT #
        self.assertEqual(actual_name, expected_name, 'Name')
        self.assertEqual(actual_arg, expected_argument, 'Argument')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
