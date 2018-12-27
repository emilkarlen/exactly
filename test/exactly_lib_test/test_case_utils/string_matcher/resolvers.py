import unittest

from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case_utils.string_matcher import resolvers as sut
from exactly_lib.test_case_utils.string_matcher.string_matchers import StringMatcherConstant
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerReference
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestWithTransformation)


class TestWithTransformation(unittest.TestCase):

    def test_references_of_transformer_and_matcher_resolver_SHOULD_be_reported(self):
        # ARRANGE #

        trans_ref_info = NameAndValue('THE_TRANSFORMER', ValueType.STRING_TRANSFORMER)
        matcher_ref_info = NameAndValue('THE_MATCHER', ValueType.STRING_MATCHER)

        expected_references = asrt.matches_sequence([
            asrt_sym_usage.matches_reference(asrt.equals(trans_ref_info.name),
                                             is_value_type_restriction(trans_ref_info.value)),
            asrt_sym_usage.matches_reference(asrt.equals(matcher_ref_info.name),
                                             is_value_type_restriction(matcher_ref_info.value)),
        ])

        resolver = sut.new_with_transformation(
            StringTransformerReference(trans_ref_info.name),
            sut.new_reference(matcher_ref_info.name),
        )
        # ACT #

        actual = resolver.references

        # ASSERT #

        expected_references.apply_without_message(self, actual)

    def test_validator_SHOULD_be_same_as_validator_of_original_matcher(self):
        # ARRANGE #

        expected_validator = pre_or_post_validation.ConstantSuccessValidator()

        original_matcher_reference = StringMatcherResolverConstantTestImpl(
            StringMatcherConstant(None),
            validator=expected_validator
        )

        transformer_resolver = StringTransformerReference('THE_TRANSFORMER')

        resolver = sut.new_with_transformation(
            transformer_resolver,
            original_matcher_reference,
        )
        # ACT #

        actual_validator = resolver.validator

        # ASSERT #

        self.assertIs(expected_validator,
                      actual_validator)
