import unittest

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.dir_dependent_value import \
    MultiDirDependentAssertion
from exactly_lib_test.type_val_deps.types.string_.test_resources import ddv_assertions as asrt_sv


def equals_list_ddv(expected: ListDdv) -> Assertion:
    return _AssertListValueHasSpecifiedProperties(expected)


class _AssertListValueHasSpecifiedProperties(MultiDirDependentAssertion):
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
                            tcds: TestCaseDs,
                            message_builder: asrt.MessageBuilder):
        assert isinstance(actual, ListDdv)
        elements_assertion = asrt.matches_sequence(self._sequence_of_element_assertions)
        elements_assertion.apply(put, actual.string_elements,
                                 message_builder.for_sub_component('elements'))
