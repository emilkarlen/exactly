import unittest

from exactly_lib.type_system_values.lines_transformer import IdentityLinesTransformer, SequenceLinesTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test),
    ])


class Test(unittest.TestCase):
    def test_construct_and_get_transformers_list(self):
        # ARRANGE #
        t_1 = IdentityLinesTransformer()
        t_2 = IdentityLinesTransformer()
        transformers_given_to_constructor = [t_1, t_2]

        # ACT #

        sequence = SequenceLinesTransformer(transformers_given_to_constructor)
        transformers_from_sequence = sequence.transformers

        # ASSERT #

        self.assertEqual(transformers_given_to_constructor,
                         list(transformers_from_sequence))
