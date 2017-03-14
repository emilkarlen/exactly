import unittest

from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.value_definition import value_definition_usage as vd
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import value_reference as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEquals(),
        unittest.makeSuite(TestNotEquals),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            vd.ValueReferenceOfPath('reffed-name',
                                    PathRelativityVariants({rel_option_type, RelOptionType.REL_ACT},
                                                           absolute))
            for absolute in [False, True]
            for rel_option_type in RelOptionType
            ]

        for value in test_cases:
            with self.subTest(msg='RelOptionTypes={}, absolute={}'.format(value.valid_relativities.rel_option_types,
                                                                          value.valid_relativities.absolute)):
                sut.equals_value_reference(value).apply_with_message(self, value, 'Equals')


class TestNotEquals(unittest.TestCase):
    def test_differs__absolute(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = vd.ValueReferenceOfPath('reffed-name',
                                           PathRelativityVariants({RelOptionType.REL_CWD}, False))
        actual = vd.ValueReferenceOfPath('reffed-name',
                                         PathRelativityVariants({RelOptionType.REL_CWD}, True))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value_reference(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__rel_option_types(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = vd.ValueReferenceOfPath('reffed-name',
                                           PathRelativityVariants({RelOptionType.REL_CWD}, False))
        actual = vd.ValueReferenceOfPath('reffed-name',
                                         PathRelativityVariants({RelOptionType.REL_HOME}, False))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value_reference(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__refs_rel_option_types(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = vd.ValueReferenceOfPath('reffed-name',
                                           PathRelativityVariants({RelOptionType.REL_CWD}, False))
        actual = vd.ValueReferenceOfPath('reffed-name',
                                         PathRelativityVariants({RelOptionType.REL_HOME}, False))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value_reference(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = vd.ValueReferenceOfPath('reffed-name',
                                           PathRelativityVariants({RelOptionType.REL_CWD}, False))
        actual = vd.ValueReferenceOfPath('OTHER-reffed-name',
                                         PathRelativityVariants({RelOptionType.REL_CWD}, False))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_value_reference(expected).apply_with_message(put, actual, 'NotEquals')
