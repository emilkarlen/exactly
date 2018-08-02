import pathlib
import unittest

from exactly_lib.section_document.source_location import SourceLocation
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.section_document.test_resources import element_assertions as sut
from exactly_lib_test.section_document.test_resources.elements import new_empty, new_comment, new_instruction
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
        actual = new_empty(line_num, line_text)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_empty_element(line_num, line_text)
        cases = [
            NameAndValue('unexpected line num',
                         new_empty(line_num + 1, line_text)
                         ),
            NameAndValue('unexpected line text',
                         new_empty(line_num, line_text + ' unexpected')
                         ),
            NameAndValue('unexpected element type - comment',
                         new_comment(line_num, line_text)
                         ),
            NameAndValue('unexpected element type - instruction',
                         new_instruction(line_num, line_text,
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
        actual = new_comment(line_num, line_text)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        line_num = 1
        line_text = 'line text'
        assertion = sut.equals_comment_element(line_num, line_text)
        cases = [
            NameAndValue('unexpected line num',
                         new_comment(line_num + 1, line_text)
                         ),
            NameAndValue('unexpected line text',
                         new_comment(line_num, line_text + ' unexpected')
                         ),
            NameAndValue('unexpected element type - empty',
                         new_empty(line_num, line_text)
                         ),
            NameAndValue('unexpected element type - instruction',
                         new_instruction(line_num, line_text,
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
        expected_file_path = pathlib.Path('a path')
        expected_file_inclusion_chain = [SourceLocation(single_line_sequence(2, 'inclusion line'),
                                                        pathlib.Path('inclusion file path'))]
        expected_abs_path_of_dir_containing_file = pathlib.Path(pathlib.Path.cwd().root)
        assertion = sut.equals_instruction_without_description(expected_line_num,
                                                               expected_line_text,
                                                               expected_section_name,
                                                               expected_file_path,
                                                               expected_file_inclusion_chain)
        actual = new_instruction(expected_line_num,
                                 expected_line_text,
                                 expected_section_name,
                                 expected_file_path,
                                 expected_abs_path_of_dir_containing_file,
                                 expected_file_inclusion_chain)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        expected_line_num = 2
        expected_line_text = 'line text'
        expected_section_name = 'section name'
        expected_file_path = pathlib.Path('a path')
        expected_file_inclusion_chain = [SourceLocation(single_line_sequence(2, 'inclusion line'),
                                                        pathlib.Path('inclusion file path'))]
        expected_abs_path_of_dir_containing_file = pathlib.Path(pathlib.Path.cwd().root)
        unexpected_abs_path_of_dir_containing_file = expected_abs_path_of_dir_containing_file / 'unexpected'
        assertion = sut.equals_instruction_without_description(expected_line_num,
                                                               expected_line_text,
                                                               expected_section_name,
                                                               expected_file_path,
                                                               expected_file_inclusion_chain)
        cases = [
            NameAndValue('unexpected line num',
                         new_instruction(expected_line_num + 1,
                                         expected_line_text,
                                         expected_section_name,
                                         expected_file_path,
                                         expected_abs_path_of_dir_containing_file,
                                         expected_file_inclusion_chain)
                         ),
            NameAndValue('unexpected line text',
                         new_instruction(expected_line_num,
                                         expected_line_text + ' unexpected',
                                         expected_section_name,
                                         expected_file_path,
                                         expected_abs_path_of_dir_containing_file,
                                         expected_file_inclusion_chain)
                         ),
            NameAndValue('unexpected section name',
                         new_instruction(expected_line_num,
                                         expected_line_text,
                                         expected_section_name + ' unexpected',
                                         expected_file_path,
                                         expected_abs_path_of_dir_containing_file,
                                         expected_file_inclusion_chain)
                         ),
            NameAndValue('unexpected file path',
                         new_instruction(expected_line_num,
                                         expected_line_text,
                                         expected_section_name,
                                         expected_file_path / 'unexpected',
                                         expected_abs_path_of_dir_containing_file,
                                         expected_file_inclusion_chain)
                         ),
            NameAndValue('unexpected abs path of dir containing file',
                         new_instruction(expected_line_num,
                                         expected_line_text,
                                         expected_section_name,
                                         expected_file_path / 'unexpected',
                                         unexpected_abs_path_of_dir_containing_file,
                                         expected_file_inclusion_chain)
                         ),
            NameAndValue('unexpected file inclusion chain',
                         new_instruction(expected_line_num,
                                         expected_line_text,
                                         expected_section_name,
                                         expected_file_path,
                                         expected_abs_path_of_dir_containing_file,
                                         [])
                         ),
            NameAndValue('unexpected element type - empty',
                         new_empty(expected_line_num, expected_line_text)
                         ),
            NameAndValue('unexpected element type - comment',
                         new_comment(expected_line_num, expected_line_text)
                         ),
        ]
        for nav in cases:
            with self.subTest(nav.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nav.value)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
