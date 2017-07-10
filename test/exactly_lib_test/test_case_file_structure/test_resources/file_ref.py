import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import SingleDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    SingleDirDependentValueAssertion
from exactly_lib_test.test_case_file_structure.test_resources.path_relativity import equals_path_relativity
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_file_ref(expected: FileRef) -> asrt.ValueAssertion:
    return _AssertFileRefHasSpecifiedProperties(expected)


class _AssertFileRefHasSpecifiedProperties(SingleDirDependentValueAssertion):
    def __init__(self, expected: FileRef):
        super().__init__(expected)
        self._expected = expected

    def _check_custom_type(self,
                           put: unittest.TestCase,
                           actual,
                           message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual, FileRef,
                             message_builder.apply('Actual value is expected to be a ' + str(FileRef)))

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: SingleDirDependentValue,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        super()._check_custom(put, actual, home_and_sds, message_builder)
        assert isinstance(actual, FileRef)

        self._check_path_suffix(put,
                                actual,
                                message_builder.for_sub_component('path_suffix'))

        self._check_relativity(put, actual, message_builder)

    def _check_path_suffix(self,
                           put: unittest.TestCase,
                           actual: FileRef,
                           message_builder: asrt.MessageBuilder):
        path_suffix = self._expected.path_suffix()
        equals_path_part(path_suffix).apply(put,
                                            actual.path_suffix(),
                                            message_builder)

    def _check_relativity(self,
                          put: unittest.TestCase,
                          actual_file_ref: FileRef,
                          message_builder: asrt.MessageBuilder):
        expected = self._expected.relativity()
        actual = actual_file_ref.relativity()
        assertion = equals_path_relativity(expected)
        assertion.apply(put, actual, message_builder.for_sub_component('specific_relativity'))
