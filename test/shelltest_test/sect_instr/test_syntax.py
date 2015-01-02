__author__ = 'emil'

import unittest

from shelltest.sect_instr import syntax


class TestExtractPhaseNameFromPhaseLine(unittest.TestCase):

    def test_valid_phase_line_without_initial_space(self):
        name = 'name'
        actual = syntax.extract_phase_name_from_phase_line(syntax.phase_header(name))
        self.assertEqual(name, actual)

    def test_valid_special_characters(self):
        name = 'begin -_.0123456789'
        actual = syntax.extract_phase_name_from_phase_line(syntax.phase_header(name))
        self.assertEqual(name, actual)

    def test_valid_phase_line_with_initial_space(self):
        actual = syntax.extract_phase_name_from_phase_line('       [name]')
        expected = 'name'
        self.assertEqual(expected, actual)

    def test_valid_phase_line_with_trailing_space(self):
        actual = syntax.extract_phase_name_from_phase_line('[name]         ')
        expected = 'name'
        self.assertEqual(expected, actual)

    def test_invalid_characters_in_name(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[! is not allowed in names]')

    def test_name_must_not_be_empty(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[]')

    def test_name_must_not_begin_with_space(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[ bad]')

    def test_name_must_not_end_with_space(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[bad ]')

    def test_name_must_be_surrounded_by_markers(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[missing_right_bracket')

    def test_right_bracket_can_only_be_followed_by_space(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[invalid-content-after-header] only space is allowed')

    def test_right_bracket_can_not_be_followed_by_a_comment(self):
        self.assertRaises(syntax.GeneralError,
                          syntax.extract_phase_name_from_phase_line,
                          '[invalid-content-after-header]#not even a comment is allowed')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestExtractPhaseNameFromPhaseLine))
    return ret_val


if __name__ == '__main__':
    unittest.main()
