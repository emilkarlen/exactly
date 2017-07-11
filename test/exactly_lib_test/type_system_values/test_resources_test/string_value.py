import unittest

from exactly_lib.type_system_values import concrete_string_values as csv
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails
from exactly_lib_test.type_system_values.test_resources import string_value as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFragment),
        unittest.makeSuite(TestEqualsStringValue),
    ])


class TestEqualsFragment(unittest.TestCase):
    # Few tests here, since the sut has been tested indirectly
    # as it is a slight modification of a generic utility that has been tested elsewhere.

    def test_pass(self):
        actual = csv.ConstantFragment('fragment value')
        expected = AMultiDirDependentValue(
            resolving_dependencies=set(),
            value_when_no_dir_dependencies=do_return('fragment value'),
            value_of_any_dependency=do_return('fragment value'))

        assertion = sut.equals_string_fragment(expected)
        assertion.apply_without_message(self, actual)

    def test_fail(self):
        actual = csv.ConstantFragment('actual value')
        expected = AMultiDirDependentValue(
            resolving_dependencies=set(),
            value_when_no_dir_dependencies=do_return('expected value'),
            value_of_any_dependency=do_return('expected value'))
        assertion = sut.equals_string_fragment(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsStringValue(unittest.TestCase):
    # Few tests here, since the sut has been tested indirectly
    # as it is a slight modification of a generic utility that has been tested elsewhere.

    def test_pass(self):
        cases = [
            (
                'no fragments',
                sut.StringValue(tuple([])),
            ),
            (
                'single fragment',
                sut.StringValue(tuple([csv.ConstantFragment('fragment value')])),
            ),
        ]
        for name, value in cases:
            with self.subTest(name=name):
                assertion = sut.equals_string_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__different_number_of_fragments(self):
        actual = sut.StringValue(tuple([]))
        expected = sut.StringValue(tuple([csv.ConstantFragment('fragment value')]))

        assertion = sut.equals_string_value(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_fail__different_fragment_value(self):
        actual = sut.StringValue(tuple([csv.ConstantFragment('actual fragment value')]))
        expected = sut.StringValue(tuple([csv.ConstantFragment('expected fragment value')]))

        assertion = sut.equals_string_value(expected)
        assert_that_assertion_fails(assertion, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
