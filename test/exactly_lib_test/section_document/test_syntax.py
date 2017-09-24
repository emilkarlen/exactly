import unittest

from exactly_lib.section_document import syntax


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestExtractSectionNameFromSectionLine)


class TestExtractSectionNameFromSectionLine(unittest.TestCase):
    def test_valid_phase_line_without_initial_space(self):
        name = 'name'
        actual = syntax.extract_section_name_from_section_line(syntax.section_header(name))
        self.assertEqual(name, actual)

    def test_valid_special_characters(self):
        name = 'begin -_.0123456789'
        actual = syntax.extract_section_name_from_section_line(syntax.section_header(name))
        self.assertEqual(name, actual)

    def test_valid_phase_line_with_initial_space(self):
        actual = syntax.extract_section_name_from_section_line('       [name]')
        expected = 'name'
        self.assertEqual(expected, actual)

    def test_valid_phase_line_with_trailing_space(self):
        actual = syntax.extract_section_name_from_section_line('[name]         ')
        expected = 'name'
        self.assertEqual(expected, actual)

    def test_invalid_characters_in_name(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[! is not allowed in names]')

    def test_name_must_not_be_empty(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[]')

    def test_name_must_not_begin_with_space(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[ bad]')

    def test_name_must_not_end_with_space(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[bad ]')

    def test_name_must_be_surrounded_by_markers(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[missing_right_bracket')

    def test_right_bracket_can_only_be_followed_by_space(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[invalid-content-after-header] only space is allowed')

    def test_right_bracket_can_not_be_followed_by_a_comment(self):
        self.assertRaises(ValueError,
                          syntax.extract_section_name_from_section_line,
                          '[invalid-content-after-header]#not even a comment is allowed')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
