import unittest

from exactly_lib.impls.types.string_transformer.impl import identity as sut
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_SHOULD_be_identity_transformer(self):
        transformer = sut.IdentityStringTransformer()
        self.assertTrue(transformer.is_identity_transformer)

    def test_empty_list_of_lines(self):
        # ARRANGE #
        input_lines = []
        model = string_sources.of_lines__w_check_for_validity(self, input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_sources.as_lines_list__w_lines_validation(self, actual)

        expected_lines = []

        self.assertEqual(expected_lines,
                         actual_lines)

    def test_non_empty_list_of_lines(self):
        # ARRANGE #
        input_lines = with_appended_new_lines([
            'we are here and they are here too',
            'here I am',
            'I am here',
        ])
        model = string_sources.of_lines__w_check_for_validity(self, input_lines)
        transformer = sut.IdentityStringTransformer()
        # ACT #

        actual = transformer.transform(model)

        # ASSERT #

        actual_lines = string_sources.as_lines_list__w_lines_validation(self, actual)

        self.assertEqual(input_lines,
                         actual_lines)
