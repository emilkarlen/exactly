import unittest

from exactly_lib.section_document.element_parsers.token_stream import TokenStream, LookAheadState
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import Token
from exactly_lib_test.section_document.element_parsers.test_resources import token_stream_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test),
        unittest.makeSuite(TestLookAheadState),
    ])


class Test(unittest.TestCase):
    def test_pass_when_no_explicit_component_assertion(self):
        test_cases = [
            NameAndValue('Empty source', ''),
            NameAndValue('Single token source', 'a_token'),
            NameAndValue('Two token source', 'first_token second'),
        ]
        for test_case in test_cases:
            with self.subTest(test_case.name):
                # ARRANGE #
                token_stream = TokenStream(test_case.value)
                assertion = sut.assert_token_stream()
                # ACT & ASSERT #
                assertion.apply_without_message(self, token_stream)

    def test_source_fail(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(source=asrt.equals('not the source'))
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_source_pass(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(source=asrt.equals('a_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_remaining_source_fail(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(remaining_source=asrt.equals('not remaining source'))
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_remaining_source_pass(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(remaining_source=asrt.equals('a_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_remaining_part_of_current_line_fail(self):
        # ARRANGE #
        token_stream = TokenStream('first line\nsecond line')
        assertion = sut.assert_token_stream(remaining_part_of_current_line=asrt.equals('second line'))
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_remaining_part_of_current_line_pass(self):
        # ARRANGE #
        token_stream = TokenStream('first line\nsecond line')
        assertion = sut.assert_token_stream(remaining_part_of_current_line=asrt.equals('first line'))
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_remaining_source_after_head_fail(self):
        # ARRANGE #
        token_stream = TokenStream('fst_token snd_token')
        assertion = sut.assert_token_stream(remaining_source_after_head=asrt.equals('fst_token'))
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_remaining_source_after_head_pass(self):
        # ARRANGE #
        token_stream = TokenStream('fst_token snd_token')
        assertion = sut.assert_token_stream(remaining_source_after_head=asrt.equals('snd_token'))
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_is_null_fail(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(is_null=asrt.is_true)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_is_null_pass(self):
        # ARRANGE #
        token_stream = TokenStream('')
        assertion = sut.assert_token_stream(is_null=asrt.is_true)
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_head_token_fail(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        failing_token_assertion = asrt.sub_component('token_type',
                                                     Token.is_quoted.fget,
                                                     asrt.is_true)
        assertion = sut.assert_token_stream(head_token=failing_token_assertion)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_head_token_pass(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        passing_token_assertion = asrt.sub_component('token_type',
                                                     Token.is_quoted.fget,
                                                     asrt.is_false)
        assertion = sut.assert_token_stream(head_token=passing_token_assertion)
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)

    def test_position_fail(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(position=asrt.equals(2))
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, token_stream)

    def test_position_pass(self):
        # ARRANGE #
        token_stream = TokenStream('a_token')
        assertion = sut.assert_token_stream(position=asrt.equals(0))
        # ACT & ASSERT #
        assertion.apply_without_message(self, token_stream)


class TestLookAheadState(unittest.TestCase):
    def test_fail(self):
        # ARRANGE #
        assertion = sut.assert_token_stream(look_ahead_state=asrt.is_(LookAheadState.NULL))
        # ACT & ASSERT #
        token_stream = TokenStream('a_token')
        self.assertTrue(token_stream.look_ahead_state is LookAheadState.HAS_TOKEN,
                        'sanity check: this test assumes that the constructor of the token parser '
                        'sets correct look-ahead state')
        assert_that_assertion_fails(assertion, token_stream)

    def test_look_ahead_state_pass(self):
        # ARRANGE #
        assertion = sut.assert_token_stream(look_ahead_state=asrt.is_(LookAheadState.NULL))
        # ACT & ASSERT #
        token_stream = TokenStream('')
        self.assertTrue(token_stream.look_ahead_state is LookAheadState.NULL,
                        'sanity check: this test assumes that the constructor of the token parser '
                        'sets correct look-ahead state')
        assertion.apply_without_message(self, token_stream)
