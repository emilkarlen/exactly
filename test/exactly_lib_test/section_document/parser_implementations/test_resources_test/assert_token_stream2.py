import unittest

from exactly_lib.section_document.parser_implementations.token import Token
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib_test.section_document.parser_implementations import test_resources as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_pass_when_no_explicit_component_assertion(self):
        test_cases = [
            ('', 'Empty source'),
            ('a_token', 'Single token source'),
            ('first_token second', 'Two token source'),
        ]
        for source, description in test_cases:
            with self.subTest(msg=description):
                # ARRANGE #
                put = test_case_with_failure_exception_set_to_test_exception()
                token_stream = TokenStream2(source)
                assertion = sut.assert_token_stream2()
                # ACT & ASSERT #
                assertion.apply_without_message(put, token_stream)

    def test_source_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(source=asrt.equals('not the source'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_source_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(source=asrt.equals('a_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_remaining_source_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(remaining_source=asrt.equals('not remaining source'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_remaining_source_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(remaining_source=asrt.equals('a_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_remaining_part_of_current_line_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('first line\nsecond line')
        assertion = sut.assert_token_stream2(remaining_part_of_current_line=asrt.equals('second line'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_remaining_part_of_current_line_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('first line\nsecond line')
        assertion = sut.assert_token_stream2(remaining_part_of_current_line=asrt.equals('first line'))
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_remaining_source_after_head_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('fst_token snd_token')
        assertion = sut.assert_token_stream2(remaining_source_after_head=asrt.equals('fst_token'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_remaining_source_after_head_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('fst_token snd_token')
        assertion = sut.assert_token_stream2(remaining_source_after_head=asrt.equals('snd_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_is_null_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(is_null=asrt.is_true)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_is_null_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('')
        assertion = sut.assert_token_stream2(is_null=asrt.is_true)
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_head_token_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        failing_token_assertion = asrt.sub_component('token_type',
                                                     Token.is_quoted.fget,
                                                     asrt.is_true)
        assertion = sut.assert_token_stream2(head_token=failing_token_assertion)
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_head_token_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        passing_token_assertion = asrt.sub_component('token_type',
                                                     Token.is_quoted.fget,
                                                     asrt.is_false)
        assertion = sut.assert_token_stream2(head_token=passing_token_assertion)
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)

    def test_position_fail(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(position=asrt.equals(2))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, token_stream)

    def test_position_pass(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        token_stream = TokenStream2('a_token')
        assertion = sut.assert_token_stream2(position=asrt.equals(0))
        # ACT & ASSERT #
        assertion.apply_without_message(put, token_stream)
