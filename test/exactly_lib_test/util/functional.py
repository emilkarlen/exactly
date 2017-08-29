import operator
import unittest

from exactly_lib.util import functional as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestComposition),
        unittest.makeSuite(TestCombineFirstAndSecond),
        unittest.makeSuite(TestAndPredicate),
    ])


class TestComposition(unittest.TestCase):
    def test(self):
        composition = sut.Composition(operator.neg, len)
        actual = composition(['a', 'b'])
        self.assertEqual(-2,
                         actual)


class TestCombineFirstAndSecond(unittest.TestCase):
    def test(self):
        composition = sut.compose_first_and_second(len, operator.neg)
        actual = composition(['a', 'b'])
        self.assertEqual(-2,
                         actual)


class TestAndPredicate(unittest.TestCase):
    def test_WHEN_no_sub_predicates_THEN_result_SHOULD_be_true(self):
        predicate = sut.and_predicate([])
        actual = predicate('anything')
        self.assertTrue(actual)

    def test_WHEN_single_predicate_THEN_result_SHOULD_be_identical_to_result_of_sub_predicate(self):
        cases = [
            (
                True,
                lambda x: True
            ),
            (
                False,
                lambda x: False
            ),
        ]
        for expected_result, sub_predicate in cases:
            with self.subTest(expected_result=expected_result):
                # ARRANGE #
                predicate = sut.and_predicate([sub_predicate])
                # ACT #
                actual = predicate('anything')
                # ASSERT #
                self.assertEqual(expected_result, actual)

    def test_WHEN_single_predicate_THEN_argument_SHOULD_be_given_to_sub_predicate(self):
        for argument_to_predicate in [False, True]:
            with self.subTest(argument_to_predicate=argument_to_predicate):
                # ARRANGE #
                predicate = sut.and_predicate([lambda x: x])
                # ACT #
                actual = predicate(argument_to_predicate)
                # ASSERT #
                self.assertEqual(argument_to_predicate, actual)

    def test_WHEN_more_than_one_predicate_THEN_argument_SHOULD_be_given_to_each_sub_predicate(self):
        for argument_to_predicate in [False, True]:
            with self.subTest(argument_to_predicate=argument_to_predicate):
                # ARRANGE #
                predicate = sut.and_predicate([lambda x: x,
                                               lambda x: x])
                # ACT #
                actual = predicate(argument_to_predicate)
                # ASSERT #
                self.assertEqual(argument_to_predicate, actual)

    def test_WHEN_more_than_one_predicate_THEN_result_SHOULD_be_combination_of_sub_results(self):
        for first_result in [False, True]:
            for second_result in [False, True]:
                expected_result = first_result and second_result
                with self.subTest(first_result=first_result,
                                  second_result=second_result):
                    # ARRANGE #
                    predicate = sut.and_predicate([lambda x: first_result,
                                                   lambda x: second_result])
                    # ACT #
                    actual = predicate('anything')
                    # ASSERT #
                    self.assertEqual(expected_result, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
