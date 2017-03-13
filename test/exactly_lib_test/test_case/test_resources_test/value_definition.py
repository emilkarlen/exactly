import unittest

from exactly_lib.test_case import value_definition as vd
from exactly_lib.util.line_source import Line
from exactly_lib_test.test_case.test_resources import file_ref as fr_tr
from exactly_lib_test.test_case.test_resources import value_definition as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEquals),
        unittest.makeSuite(TestNotEquals),
    ])


class TestEquals(unittest.TestCase):
    def test_equal__NOT_ignore_source_line(self):
        value = vd.ValueDefinitionOfPath('vd-name',
                                         vd.FileRefValue(Line(1, 'source code'),
                                                         fr_tr.file_ref_test_impl('file-name-component')))

        sut.equals_value_definition(value, ignore_source_line=False).apply_with_message(self, value, 'Equals')

    def test_differing_source_line__ignore_source_line(self):
        value_line_1 = vd.ValueDefinitionOfPath('vd-name',
                                                vd.FileRefValue(Line(1, 'source code'),
                                                                fr_tr.file_ref_test_impl('file-name-component')))

        value_line_2 = vd.ValueDefinitionOfPath('vd-name',
                                                vd.FileRefValue(Line(2, 'source code'),
                                                                fr_tr.file_ref_test_impl('file-name-component')))

        sut.equals_value_definition(value_line_1,
                                    ignore_source_line=True).apply_with_message(self,
                                                                                value_line_2,
                                                                                'Equals')


class TestNotEquals(unittest.TestCase):
    def test_only_difference_is_source_line__NOT_ignore_source_line(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        common_file_ref = fr_tr.file_ref_test_impl('file-name-component')
        common_name = 'vd-name'
        value_line_1 = vd.ValueDefinitionOfPath(common_name,
                                                vd.FileRefValue(Line(1, 'source code'),
                                                                common_file_ref))

        value_line_2 = vd.ValueDefinitionOfPath(common_name,
                                                vd.FileRefValue(Line(2, 'source code'),
                                                                common_file_ref))
        with put.assertRaises(TestException):
            sut.equals_value_definition(value_line_1,
                                        ignore_source_line=False).apply_with_message(put,
                                                                                     value_line_2,
                                                                                     'NOT Equals')

    def test_only_difference_is_name__ignore_source_line(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref_value = vd.FileRefValue(Line(1, 'source code'),
                                         fr_tr.file_ref_test_impl('file-name-component'))
        expected = vd.ValueDefinitionOfPath('EXPECTED name', file_ref_value)
        actual = vd.ValueDefinitionOfPath('ACTUAL name', file_ref_value)
        with put.assertRaises(TestException):
            sut.equals_value_definition(expected,
                                        ignore_source_line=True).apply_with_message(put,
                                                                                    actual,
                                                                                    'NOT Equals')

    def test_only_difference_is_name__NOT_ignore_source_line(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref_value = vd.FileRefValue(Line(1, 'source code'),
                                         fr_tr.file_ref_test_impl('file-name-component'))
        expected = vd.ValueDefinitionOfPath('EXPECTED name', file_ref_value)
        actual = vd.ValueDefinitionOfPath('ACTUAL name', file_ref_value)
        with put.assertRaises(TestException):
            sut.equals_value_definition(expected,
                                        ignore_source_line=False).apply_with_message(put,
                                                                                     actual,
                                                                                     'NOT Equals')

    def test_only_difference_is_file_ref__ignore_source_line(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref_e = fr_tr.file_ref_test_impl('file-name-of-EXPECTED')
        file_ref_a = fr_tr.file_ref_test_impl('file-name-of-ACTUAL')
        common_source = Line(1, 'source code')
        common_name = 'name'
        expected = vd.ValueDefinitionOfPath(common_name, vd.FileRefValue(common_source, file_ref_e))
        actual__ = vd.ValueDefinitionOfPath(common_name, vd.FileRefValue(common_source, file_ref_a))
        with put.assertRaises(TestException):
            sut.equals_value_definition(expected,
                                        ignore_source_line=True).apply_with_message(put,
                                                                                    actual__,
                                                                                    'NOT Equals')

    def test_only_difference_is_file_ref__NOT_ignore_source_line(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref_e = fr_tr.file_ref_test_impl('file-name-of-EXPECTED')
        file_ref_a = fr_tr.file_ref_test_impl('file-name-of-ACTUAL')
        common_source = Line(1, 'source code')
        common_name = 'name'
        expected = vd.ValueDefinitionOfPath(common_name, vd.FileRefValue(common_source, file_ref_e))
        actual__ = vd.ValueDefinitionOfPath(common_name, vd.FileRefValue(common_source, file_ref_a))
        with put.assertRaises(TestException):
            sut.equals_value_definition(expected,
                                        ignore_source_line=False).apply_with_message(put,
                                                                                     actual__,
                                                                                     'NOT Equals')
