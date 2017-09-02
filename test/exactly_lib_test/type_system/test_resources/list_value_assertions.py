import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.list_value import ListValue
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import MultiDirDependentValueAssertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.test_resources import string_value_assertions as asrt_sv


def equals_list_value(expected: ListValue) -> asrt.ValueAssertion:
    return _AssertListValueHasSpecifiedProperties(expected)


class _AssertListValueHasSpecifiedProperties(MultiDirDependentValueAssertion):
    def __init__(self, expected: ListValue):
        super().__init__(ListValue, expected)
        self._expected = expected
        self._sequence_of_element_assertions = []
        for idx, element in enumerate(expected.string_value_elements):
            assert isinstance(element, StringValue), 'Element must be a StringValue #' + str(idx)
            self._sequence_of_element_assertions.append(asrt_sv.equals_string_value(element))

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDirDependentValue,
                            home_and_sds: HomeAndSds,
                            message_builder: asrt.MessageBuilder):
        assert isinstance(actual, ListValue)
        elements_assertion = asrt.matches_sequence(self._sequence_of_element_assertions)
        elements_assertion.apply(put, actual.string_value_elements,
                                 message_builder.for_sub_component('elements'))
