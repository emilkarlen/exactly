import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import MultiDirDependentValueAssertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources import string_ddv_assertions as asrt_sv


def equals_list_ddv(expected: ListDdv) -> ValueAssertion:
    return _AssertListValueHasSpecifiedProperties(expected)


class _AssertListValueHasSpecifiedProperties(MultiDirDependentValueAssertion):
    def __init__(self, expected: ListDdv):
        super().__init__(ListDdv, expected)
        self._expected = expected
        self._sequence_of_element_assertions = []
        for idx, element in enumerate(expected.string_elements):
            assert isinstance(element, StringDdv), 'Element must be a StringDdv #' + str(idx)
            self._sequence_of_element_assertions.append(asrt_sv.equals_string_ddv(element))

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDependenciesDdv,
                            tcds: Tcds,
                            message_builder: asrt.MessageBuilder):
        assert isinstance(actual, ListDdv)
        elements_assertion = asrt.matches_sequence(self._sequence_of_element_assertions)
        elements_assertion.apply(put, actual.string_elements,
                                 message_builder.for_sub_component('elements'))