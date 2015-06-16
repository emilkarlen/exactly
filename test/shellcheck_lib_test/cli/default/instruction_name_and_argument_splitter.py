import unittest

from shellcheck_lib.cli.default.instruction_name_and_argument_splitter import splitter


class TestCase(unittest.TestCase):
    def test_single_character_name_and_no_argument(self):
        self._check('i', 'i', '')

    def test_multi_character_name_and_no_argument(self):
        self._check('instruction',
                    'instruction',
                    '')

    def _check(self,
               line: str,
               expected_name: str,
               expected_argument: str):
        # ACT #
        (actual_name, actual_arg) = splitter(line)
        # ASSERT #
        self.assertEqual(expected_name, actual_name, 'Name')
        self.assertEqual(expected_argument, actual_arg, 'Argument')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


if __name__ == '__main__':
    unittest.main()
