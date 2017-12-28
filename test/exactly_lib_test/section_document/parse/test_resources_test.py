import unittest

from exactly_lib_test.section_document.parse import test_resources as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsEmptyElement),
        unittest.makeSuite(TestEqualsCommentElement),
        unittest.makeSuite(TestEqualsInstructionWithoutDescription),
    ])


class TestEqualsEmptyElement(unittest.TestCase):

    def test_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_empty_element(line_num, line_text)
        actual = sut.new_empty(line_num, line_text)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_empty_element(line_num, line_text)
        cases = [
            NameAndValue('unexpected line num',
                         sut.new_empty(line_num + 1, line_text)
                         ),
            NameAndValue('unexpected line text',
                         sut.new_empty(line_num, line_text + ' unexpected')
                         ),
            NameAndValue('unexpected element type - comment',
                         sut.new_comment(line_num, line_text)
                         ),
            NameAndValue('unexpected element type - instruction',
                         sut.new_instruction(line_num, line_text,
                                             'section name of instruction')
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nav.value)


class TestEqualsCommentElement(unittest.TestCase):

    def test_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_comment_element(line_num, line_text)
        actual = sut.new_comment(line_num, line_text)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_comment_element(line_num, line_text)
        cases = [
            NameAndValue('unexpected line num',
                         sut.new_comment(line_num + 1, line_text)
                         ),
            NameAndValue('unexpected line text',
                         sut.new_comment(line_num, line_text + ' unexpected')
                         ),
            NameAndValue('unexpected element type - empty',
                         sut.new_empty(line_num, line_text)
                         ),
            NameAndValue('unexpected element type - instruction',
                         sut.new_instruction(line_num, line_text,
                                             'section name of instruction')
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nav.value)


class TestEqualsInstructionWithoutDescription(unittest.TestCase):

    def test_matches(self):
        # ARRANGE #
        expected_line_num = 1
        expected_line_text = 'line text'
        expected_section_name = 'section name'
        assertion = sut.equals_instruction_without_description(expected_line_num,
                                                               expected_line_text,
                                                               expected_section_name)
        actual = sut.new_instruction(expected_line_num,
                                     expected_line_text,
                                     expected_section_name)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        expected_line_num = 2
        expected_line_text = 'line text'
        expected_section_name = 'section name'
        assertion = sut.equals_instruction_without_description(expected_line_num,
                                                               expected_line_text,
                                                               expected_section_name)
        cases = [
            NameAndValue('unexpected line num',
                         sut.new_instruction(expected_line_num + 1,
                                             expected_line_text,
                                             expected_section_name)
                         ),
            NameAndValue('unexpected line text',
                         sut.new_instruction(expected_line_num,
                                             expected_line_text + ' unexpected',
                                             expected_section_name)
                         ),
            NameAndValue('unexpected section name',
                         sut.new_instruction(expected_line_num,
                                             expected_line_text,
                                             expected_section_name + ' unexpected')
                         ),
            NameAndValue('unexpected element type - empty',
                         sut.new_empty(expected_line_num, expected_line_text)
                         ),
            NameAndValue('unexpected element type - comment',
                         sut.new_comment(expected_line_num, expected_line_text)
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nav.value)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
