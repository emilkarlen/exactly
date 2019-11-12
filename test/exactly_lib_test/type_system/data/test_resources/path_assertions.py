import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import Max1DependencyDdv
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    SingleDirDependentValueAssertion
from exactly_lib_test.test_case_file_structure.test_resources.path_relativity import equals_path_relativity
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources.path_part_assertions import equals_path_part


def equals_path(expected: PathDdv) -> ValueAssertion:
    return _AssertPathHasSpecifiedProperties(expected)


class _AssertPathHasSpecifiedProperties(SingleDirDependentValueAssertion):
    def __init__(self, expected: PathDdv):
        super().__init__(PathDdv, expected)
        self._expected = expected

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: Max1DependencyDdv,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        super()._check_custom(put, actual, home_and_sds, message_builder)
        assert isinstance(actual, PathDdv)

        self._check_path_suffix(put,
                                actual,
                                message_builder.for_sub_component('path_suffix'))

        self._check_relativity(put, actual, message_builder)

    def _check_path_suffix(self,
                           put: unittest.TestCase,
                           actual: PathDdv,
                           message_builder: asrt.MessageBuilder):
        path_suffix = self._expected.path_suffix()
        equals_path_part(path_suffix).apply(put,
                                            actual.path_suffix(),
                                            message_builder)

    def _check_relativity(self,
                          put: unittest.TestCase,
                          actual_path: PathDdv,
                          message_builder: asrt.MessageBuilder):
        expected = self._expected.relativity()
        actual = actual_path.relativity()
        assertion = equals_path_relativity(expected)
        assertion.apply(put, actual, message_builder.for_sub_component('specific_relativity'))
