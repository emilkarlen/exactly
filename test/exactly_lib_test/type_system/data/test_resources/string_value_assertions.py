import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.string_value import StringValue, StringFragment
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import MultiDirDependentValueAssertion
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_string_value(expected: StringValue) -> asrt.ValueAssertion:
    return _AssertStringValueHasSpecifiedProperties(expected)


def equals_string_fragment(expected: MultiDirDependentValue) -> asrt.ValueAssertion:
    return _AssertStringFragmentHasSpecifiedProperties(expected)


class _AssertStringFragmentHasSpecifiedProperties(MultiDirDependentValueAssertion):
    def __init__(self, expected: MultiDirDependentValue):
        super().__init__(StringFragment, expected)
        self._expected = expected


class _AssertStringValueHasSpecifiedProperties(MultiDirDependentValueAssertion):
    def __init__(self, expected: StringValue):
        super().__init__(StringValue, expected)
        self._expected = expected
        self._sequence_of_fragment_assertions = []
        for idx, element in enumerate(expected.fragments):
            assert isinstance(element, StringFragment), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_fragment_assertions.append(equals_string_fragment(element))

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDirDependentValue,
                            home_and_sds: HomeAndSds,
                            message_builder: asrt.MessageBuilder):
        assert isinstance(actual, StringValue)
        fragments_assertion = asrt.matches_sequence(self._sequence_of_fragment_assertions)
        fragments_assertion.apply(put, actual.fragments, message_builder.for_sub_component('fragments'))
