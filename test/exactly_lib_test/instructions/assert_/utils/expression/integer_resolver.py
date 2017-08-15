import unittest

from exactly_lib.instructions.assert_.utils.expression import integer_resolver as sut
from exactly_lib.instructions.utils.return_svh_via_exceptions import SvhValidationException
from exactly_lib.symbol import string_resolver
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidationPreSds),
        unittest.makeSuite(TestResolve),
    ])


class TestResolve(unittest.TestCase):
    def test_resolved_value_is_returned(self):
        # ARRANGE #
        expected_resolved_value = 72

        the_instruction_environment = instruction_environment.fake_post_sds_environment()

        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            string_resolver.string_constant(str(expected_resolved_value)))

        # ACT #

        actual = resolver_to_check.resolve(the_instruction_environment)

        # ASSERT #

        self.assertEqual(expected_resolved_value,
                         actual)


class TestSymbolReferences(unittest.TestCase):
    def test_no_references_SHOULD_be_reported_WHEN_string_resolver_has_no_references(self):
        # ARRANGE #

        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            string_resolver.string_constant(str(1)))

        # ACT #

        actual = resolver_to_check.references

        # ASSERT #

        self.assertEqual([], actual,
                         'no references should be reported')

    def test_references_of_string_resolver_SHOULD_be_reported(self):
        # ARRANGE #

        reference_of_string_resolver = symbol_utils.symbol_reference('symbol name')

        the_string_resolver = string_resolver.symbol_reference(reference_of_string_resolver)

        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            the_string_resolver)

        # ACT #

        actual = resolver_to_check.references

        # ASSERT #

        expected_references = [reference_of_string_resolver]

        assertion = equals_symbol_references(expected_references)

        assertion.apply_without_message(self, actual)


class TestValidationPreSds(unittest.TestCase):
    def test_validation_SHOULD_fail_WHEN_resolved_value_is_not_an_integer(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()
        test_cases = [
            'a',
            'a b',
            '10 a',
            '10a',
            '1.5',
        ]
        for custom_validator in [None, do_return(None)]:
            for resolved_value in test_cases:
                with self.subTest(
                        custom_validator_is_none=str(custom_validator is None),
                        resolved_value=resolved_value):
                    # ARRANGE #
                    resolver_to_check = sut.IntegerResolver('the property to check',
                                                            string_resolver.string_constant(resolved_value),
                                                            custom_validator)
                    # ACT & ASSERT #
                    with self.assertRaises(SvhValidationException) as cm:
                        resolver_to_check.validate_pre_sds(the_instruction_environment)

                    self.assertIsInstance(cm.exception.err_msg,
                                          str,
                                          'the error message should be a str')

    def test_validation_SHOULD_fail_WHEN_custom_validator_fails(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 1

        # ARRANGE #
        error_message_from_custom_validator = 'error message'
        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            string_resolver.string_constant(str(resolved_value)),
            CustomValidator(value_that_makes_the_validation_succeed=resolved_value + 1,
                            error_message=error_message_from_custom_validator))
        # ACT & ASSERT #
        with self.assertRaises(SvhValidationException) as cm:
            resolver_to_check.validate_pre_sds(the_instruction_environment)

        self.assertEqual(error_message_from_custom_validator,
                         cm.exception.err_msg)

    def test_validation_SHOULD_succeed_WHEN_value_is_an_integer_and_custom_validator_succeeds(self):
        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 1

        cases = [
            None,
            CustomValidator(value_that_makes_the_validation_succeed=resolved_value,
                            error_message='error message from custom validator')
        ]
        for custom_validator in cases:
            resolver_to_check = sut.IntegerResolver(
                'the property to check',
                string_resolver.string_constant(str(resolved_value)),
                custom_validator)
            with self.subTest(custom_validator_is_none=str(custom_validator is None)):
                resolver_to_check.validate_pre_sds(the_instruction_environment)


class CustomValidator:
    def __init__(self, value_that_makes_the_validation_succeed: int,
                 error_message: str):
        self.error_message = error_message
        self.value_that_makes_the_validation_succeed = value_that_makes_the_validation_succeed

    def __call__(self, value: int):
        if value != self.value_that_makes_the_validation_succeed:
            return self.error_message

        return None
