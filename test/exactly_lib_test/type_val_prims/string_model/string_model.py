import unittest

from exactly_lib.type_val_prims import string_model as sut
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.type_val_prims.string_model.test_resources import string_models
from exactly_lib_test.util.str_ import read_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestReadLinesAsStrWMinimumNumChars(),
    ])


class TestReadLinesAsStrWMinimumNumChars(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in read_lines.cases():
            for read_case in case.expectation:
                with self.subTest(
                        input_=case.arrangement,
                        min_num_chars_to_read=read_case.min_num_chars_to_read,
                        string=read_case.string,
                        may_have_more_contents=read_case.may_have_more_contents,
                ):
                    model = string_models.StringModelThat.new_w_defaults_of_not_impl(
                        as_lines=do_return(iter(case.arrangement))
                    )
                    # ACT #
                    contents, may_have_more = sut.read_lines_as_str__w_minimum_num_chars(
                        read_case.min_num_chars_to_read,
                        model
                    )
                    # ASSERT #
                    self.assertEqual(read_case.string, contents,
                                     'string read')
                    self.assertEqual(read_case.may_have_more_contents, may_have_more,
                                     'may have more contents')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
