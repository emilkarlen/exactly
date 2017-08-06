import unittest

from exactly_lib.default.instruction_name_and_argument_splitter import splitter


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


class TestCase(unittest.TestCase):
    def test_single_character_name_and_no_argument(self):
        self._check('i', 'i')

    def test_multi_character_name_and_no_argument(self):
        self._check('instruction',
                    'instruction')

    def test_valid_name_characters(self):
        self._check('abczABCZ01239.-$ argument',
                    'abczABCZ01239.-$')

    def test_skip_initial_space(self):
        self._check('   name argument',
                    'name')

    def test_do_not_skip_trailing_space(self):
        self._check('name :argument  ',
                    'name')

    def test_under_score(self):
        self._check('a_b c',
                    'a_b')

    def test_dollar(self):
        self._check('$ command and args',
                    '$')

    def test_raise_exception_if_no_instruction_name(self):
        with self.assertRaises(ValueError):
            splitter('     ')

    def _check(self,
               line: str,
               expected_name: str):
        # ACT #
        actual_name = splitter(line)
        # ASSERT #
        self.assertEqual(expected_name, actual_name, 'Name')


if __name__ == '__main__':
    unittest.main()
