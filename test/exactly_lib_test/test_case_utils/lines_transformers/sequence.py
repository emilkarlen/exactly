import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system_values.lines_transformer import IdentityLinesTransformer, SequenceLinesTransformer, \
    LinesTransformer
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

    def test_WHEN_single_transformer_THEN_transformer_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        tcds = fake_home_and_sds()

        to_upper_t = MyToUppercaseTransformer()

        sequence = SequenceLinesTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']

        # ACT #

        actual = sequence.transform(tcds, iter(input_lines))

        # ASSERT #

        expected = to_upper_t.transform(tcds, iter(input_lines))

        expected_as_list = list(expected)
        actual_as_list = list(actual)

        self.assertEqual(expected_as_list,
                         actual_as_list)


class MyToUppercaseTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        return map(str.upper, lines)
