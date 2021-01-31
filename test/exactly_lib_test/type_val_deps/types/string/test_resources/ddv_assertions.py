import unittest

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv, StringFragmentDdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.dir_dependent_value import \
    MultiDirDependentAssertion


def equals_string_ddv(expected: StringDdv) -> Assertion[StringDdv]:
    return _AssertStringValueHasSpecifiedProperties(expected)


def equals_string_fragment_ddv(expected: MultiDependenciesDdv) -> Assertion[StringFragmentDdv]:
    return _AssertStringFragmentHasSpecifiedProperties(expected)


class _AssertStringFragmentHasSpecifiedProperties(MultiDirDependentAssertion):
    def __init__(self, expected: MultiDependenciesDdv):
        super().__init__(StringFragmentDdv, expected)
        self._expected = expected


class _AssertStringValueHasSpecifiedProperties(MultiDirDependentAssertion):
    def __init__(self, expected: StringDdv):
        super().__init__(StringDdv, expected)
        self._expected = expected
        self._sequence_of_fragment_assertions = []
        for idx, element in enumerate(expected.fragments):
            assert isinstance(element, StringFragmentDdv), 'Element must be a StringFragment #' + str(idx)
            self._sequence_of_fragment_assertions.append(equals_string_fragment_ddv(element))

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDependenciesDdv,
                            tcds: TestCaseDs,
                            message_builder: asrt.MessageBuilder):
        assert isinstance(actual, StringDdv)
        fragments_assertion = asrt.matches_sequence(self._sequence_of_fragment_assertions)
        fragments_assertion.apply(put, actual.fragments, message_builder.for_sub_component('fragments'))
