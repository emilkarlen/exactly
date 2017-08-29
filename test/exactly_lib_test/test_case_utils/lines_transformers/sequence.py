import unittest

from exactly_lib.type_system_values.lines_transformer import IdentityLinesTransformer, SequenceLinesTransformer
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds


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

    def test_WHEN_sequence_of_transformers_is_empty_THEN_output_SHOULD_be_equal_to_input(self):
        # ARRANGE #
        tcds = fake_home_and_sds()
        sequence = SequenceLinesTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        input_iter = iter(input_lines)
        # ACT #
        output = sequence.transform(tcds, input_iter)
        # ASSERT #
        output_lines = list(output)

        self.assertEqual(input_lines,
                         output_lines)
