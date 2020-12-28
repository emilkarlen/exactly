import unittest

from exactly_lib.type_val_deps.types.string_ import strings_ddvs as csv
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_val_deps.dep_variants.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.type_val_deps.types.string.test_resources import ddv_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFragment),
        unittest.makeSuite(TestEqualsStringValue),
    ])


class TestEqualsFragment(unittest.TestCase):
    # Few tests here, since the sut has been tested indirectly
    # as it is a slight modification of a generic utility that has been tested elsewhere.

    def test_pass(self):
        actual = csv.ConstantFragmentDdv('fragment value')
        expected = AMultiDirDependentValue(
            resolving_dependencies=set(),
            get_value_when_no_dir_dependencies=do_return('fragment value'),
            get_value_of_any_dependency=do_return('fragment value'))

        assertion = sut.equals_string_fragment_ddv(expected)
        assertion.apply_without_message(self, actual)

    def test_fail(self):
        actual = csv.ConstantFragmentDdv('actual value')
        expected = AMultiDirDependentValue(
            resolving_dependencies=set(),
            get_value_when_no_dir_dependencies=do_return('expected value'),
            get_value_of_any_dependency=do_return('expected value'))
        assertion = sut.equals_string_fragment_ddv(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsStringValue(unittest.TestCase):
    # Few tests here, since the sut has been tested indirectly
    # as it is a slight modification of a generic utility that has been tested elsewhere.

    def test_pass(self):
        cases = [
            (
                'no fragments',
                sut.StringDdv(tuple([])),
            ),
            (
                'single fragment',
                sut.StringDdv(tuple([csv.ConstantFragmentDdv('fragment value')])),
            ),
        ]
        for name, value in cases:
            with self.subTest(name=name):
                assertion = sut.equals_string_ddv(value)
                assertion.apply_without_message(self, value)

    def test_fail__different_number_of_fragments(self):
        actual = sut.StringDdv(tuple([]))
        expected = sut.StringDdv(tuple([csv.ConstantFragmentDdv('fragment value')]))

        assertion = sut.equals_string_ddv(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_fail__different_fragment_value(self):
        actual = sut.StringDdv(tuple([csv.ConstantFragmentDdv('actual fragment value')]))
        expected = sut.StringDdv(tuple([csv.ConstantFragmentDdv('expected fragment value')]))

        assertion = sut.equals_string_ddv(expected)
        assert_that_assertion_fails(assertion, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
