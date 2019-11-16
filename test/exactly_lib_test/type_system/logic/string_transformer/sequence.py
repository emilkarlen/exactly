import unittest

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.string_transformer import StringTransformer, IdentityStringTransformer, \
    SequenceStringTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.string_transformers import \
    MyNonIdentityTransformer, MyToUppercaseTransformer, MyCountNumUppercaseCharactersTransformer


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPrimitiveValue)


def equals_string_transformer(expected: StringTransformer) -> ValueAssertion[StringTransformer]:
    if isinstance(expected, IdentityStringTransformer):
        return asrt.is_instance(IdentityStringTransformer)
    if isinstance(expected, SequenceStringTransformer):
        return equals_sequence_transformer(expected)
    raise TypeError('Unknown type of {}: {}'.format(StringTransformer, expected))


def equals_sequence_transformer(expected: SequenceStringTransformer) -> ValueAssertion[StringTransformer]:
    return asrt.is_instance_with(
        SequenceStringTransformer,
        asrt.sub_component('transformers',
                           SequenceStringTransformer.transformers.fget,
                           asrt.matches_sequence([
                               equals_string_transformer(lt) for lt in expected.transformers
                           ])
                           )
    )


def make_identity_transformer(tcds: Tcds) -> StringTransformer:
    return IdentityStringTransformer()


class TestPrimitiveValue(unittest.TestCase):
    def test_SHOULD_is_identity_transformer(self):
        cases = [
            (
                'empty list of transformers',
                SequenceStringTransformer([]),
                True,
            ),
            (
                'single identity transformer',
                SequenceStringTransformer([IdentityStringTransformer()]),
                True,
            ),
            (
                'multiple identity transformers',
                SequenceStringTransformer([IdentityStringTransformer(),
                                           IdentityStringTransformer()]),
                True,
            ),
            (
                'non-identity transformer',
                SequenceStringTransformer([MyNonIdentityTransformer()]),
                False,
            ),
        ]
        for case_name, transformer, expected in cases:
            with self.subTest(case_name=case_name):
                self.assertEqual(expected,
                                 transformer.is_identity_transformer,
                                 'is_identity_transformation')

    def test_construct_and_get_transformers_list(self):
        # ARRANGE #
        t_1 = IdentityStringTransformer()
        t_2 = IdentityStringTransformer()
        transformers_given_to_constructor = [t_1, t_2]

        # ACT #

        sequence = SequenceStringTransformer(transformers_given_to_constructor)
        transformers_from_sequence = sequence.transformers

        # ASSERT #

        self.assertEqual(transformers_given_to_constructor,
                         list(transformers_from_sequence))

    def test_WHEN_sequence_of_transformers_is_empty_THEN_output_SHOULD_be_equal_to_input(self):
        # ARRANGE #
        sequence = SequenceStringTransformer([])

        input_lines = ['first',
                       'second',
                       'third']
        input_iter = iter(input_lines)
        # ACT #
        output = sequence.transform(input_iter)
        # ASSERT #
        output_lines = list(output)

        self.assertEqual(input_lines,
                         output_lines)

    def test_WHEN_single_transformer_THEN_sequence_SHOULD_be_identical_to_the_single_transformer(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()

        sequence = SequenceStringTransformer([to_upper_t])

        input_lines = ['first',
                       'second',
                       'third']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['FIRST',
                                 'SECOND',
                                 'THIRD']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)

    def test_WHEN_multiple_transformers_THEN_transformers_SHOULD_be_chained(self):
        # ARRANGE #

        to_upper_t = MyToUppercaseTransformer()
        count_num_upper = MyCountNumUppercaseCharactersTransformer()

        sequence = SequenceStringTransformer([to_upper_t,
                                              count_num_upper])

        input_lines = ['this is',
                       'the',
                       'input']

        # ACT #

        actual = sequence.transform(iter(input_lines))

        # ASSERT #

        expected_output_lines = ['6',
                                 '3',
                                 '5']

        actual_as_list = list(actual)

        self.assertEqual(expected_output_lines,
                         actual_as_list)
