import unittest

from exactly_lib.default.instruction_name_and_argument_splitter import splitter


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCase))
    return ret_val


class TestCase(unittest.TestCase):
    def test_single_character_name_and_no_argument(self):
        self._check('i', 'i', '')

    def test_multi_character_name_and_no_argument(self):
        self._check('instruction',
                    'instruction',
                    '')

    def test_valid_name_characters(self):
        self._check('abczABCZ01239.-$ argument',
                    'abczABCZ01239.-$',
                    ' argument')

    def test_skip_initial_space(self):
        self._check('   name argument',
                    'name',
                    ' argument')

    def test_do_not_skip_trailing_space(self):
        self._check('name :argument  ',
                    'name',
                    ' :argument  ')

    def test_under_score(self):
        self._check('a_b c',
                    'a_b',
                    ' c')

    def test_dollar(self):
        self._check('$ command and args',
                    '$',
                    ' command and args')

    def _check(self,
               line: str,
               expected_name: str,
               expected_argument: str):
        # ACT #
        (actual_name, actual_arg) = splitter(line)
        # ASSERT #
        self.assertEqual(expected_name, actual_name, 'Name')
        self.assertEqual(expected_argument, actual_arg, 'Argument')


if __name__ == '__main__':
    unittest.main()
