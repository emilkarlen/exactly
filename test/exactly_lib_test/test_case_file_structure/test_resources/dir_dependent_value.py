import unittest
from typing import TypeVar, Callable

from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv, Max1DependencyDdv, \
    MultiDependenciesDdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase

T = TypeVar('T')


def matches_single_dir_dependent_value(expected: Max1DependencyDdv,
                                       value_assertion: Callable[[T], ValueAssertion[T]] = asrt.equals
                                       ) -> ValueAssertion[DependenciesAwareDdv[T]]:
    return SingleDirDependentValueAssertion(Max1DependencyDdv,
                                            expected,
                                            value_assertion)


def matches_multi_dir_dependent_value(expected: MultiDependenciesDdv,
                                      value_assertion_from_expected:
                                      Callable[[T], ValueAssertion[T]] = asrt.equals
                                      ) -> ValueAssertion[DependenciesAwareDdv[T]]:
    return MultiDirDependentValueAssertion(MultiDependenciesDdv,
                                           expected,
                                           value_assertion_from_expected)


class DirDependentValueAssertionBase(ValueAssertionBase[DependenciesAwareDdv[T]]):
    def __init__(self,
                 expected_type,
                 expected: DependenciesAwareDdv,
                 value_assertion_from_expected: Callable[[T], ValueAssertion[T]]):
        self._expected_type = expected_type
        self._expected = expected
        self._value_assertion_from_expected = value_assertion_from_expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        self._check_type(put, value, message_builder)
        assert isinstance(value, DependenciesAwareDdv)

        self._check_common_dependencies(put, value, message_builder)
        self._check_existence(put, value, message_builder)

        tcds = fake_tcds()
        self._check_custom_dependencies(put, value, tcds, message_builder)
        self._check_value(put, value, tcds, message_builder)

        self._check_custom(put, value, tcds, message_builder)

    def _check_type(self,
                    put: unittest.TestCase,
                    actual,
                    message_builder: asrt.MessageBuilder
                    ):
        put.assertIsInstance(actual, self._expected_type,
                             message_builder.apply('Actual value is expected to be a ' + str(self._expected_type)))

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: DependenciesAwareDdv,
                                   tcds: Tcds,
                                   message_builder: asrt.MessageBuilder):
        raise NotImplementedError()

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: DependenciesAwareDdv,
                      tcds: Tcds,
                      message_builder: asrt.MessageBuilder):
        raise NotImplementedError()

    def _check_existence(self,
                         put: unittest.TestCase,
                         actual: DependenciesAwareDdv,
                         message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.exists_pre_sds(),
                        actual.exists_pre_sds(),
                        message_builder.apply('exists_pre_sds'))

    def _check_common_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: DependenciesAwareDdv,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.has_dir_dependency(),
                        actual.has_dir_dependency(),
                        message_builder.apply('has_dir_dependency'))
        put.assertEqual(self._expected.resolving_dependencies(),
                        actual.resolving_dependencies(),
                        message_builder.apply('resolving_dependencies'))

    def _check_value(self,
                     put: unittest.TestCase,
                     actual: DependenciesAwareDdv,
                     tcds: Tcds,
                     message_builder: asrt.MessageBuilder):
        if not self._expected.has_dir_dependency():
            expected = self._expected.value_when_no_dir_dependencies()
            assertion = self._value_assertion_from_expected(expected)
            assertion.apply(put,
                            actual.value_when_no_dir_dependencies(),
                            message_builder.for_sub_component('value_when_no_dir_dependencies'))

        expected = self._expected.value_of_any_dependency(tcds)
        assertion = self._value_assertion_from_expected(expected)
        assertion.apply(put,
                        actual.value_of_any_dependency(tcds),
                        message_builder.for_sub_component('value_of_any_dependency'))


class SingleDirDependentValueAssertion(DirDependentValueAssertionBase):
    def __init__(self,
                 expected_type,
                 expected: Max1DependencyDdv,
                 value_assertion_from_expected: Callable[[T], ValueAssertion[T]] = asrt.equals):
        super().__init__(expected_type, expected, value_assertion_from_expected)
        self._expected_single_dep_value = expected

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: Max1DependencyDdv,
                                   tcds: Tcds,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_single_dep_value.resolving_dependency(),
                        actual.resolving_dependency(),
                        message_builder.apply('resolving_dependency'))

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: Max1DependencyDdv,
                      tcds: Tcds,
                      message_builder: asrt.MessageBuilder):
        if self._expected.exists_pre_sds():
            put.assertEqual(self._expected_single_dep_value.value_pre_sds(tcds.hds),
                            actual.value_pre_sds(tcds.hds),
                            message_builder.apply('value_pre_sds'))
        else:
            put.assertEqual(self._expected_single_dep_value.value_post_sds(tcds.sds),
                            actual.value_post_sds(tcds.sds),
                            message_builder.apply('value_post_sds'))
        self._check_custom_single(put, actual, tcds, message_builder)

    def _check_custom_single(self,
                             put: unittest.TestCase,
                             actual: Max1DependencyDdv,
                             tcds: Tcds,
                             message_builder: asrt.MessageBuilder):
        pass


class MultiDirDependentValueAssertion(DirDependentValueAssertionBase):
    def __init__(self,
                 expected_type,
                 expected: MultiDependenciesDdv,
                 value_assertion_from_expected: Callable[[T], ValueAssertion[T]] = asrt.equals):
        super().__init__(expected_type, expected, value_assertion_from_expected)
        self._expected_multi_dep_value = expected

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: MultiDependenciesDdv,
                                   tcds: Tcds,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_multi_dep_value.dir_dependencies(),
                        actual.dir_dependencies(),
                        message_builder.apply('dir_dependency'))

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: MultiDependenciesDdv,
                      tcds: Tcds,
                      message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_multi_dep_value.dir_dependencies(),
                        actual.dir_dependencies(),
                        'dir_dependency')

        self._check_custom_multi(put, actual, tcds, message_builder)

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDependenciesDdv,
                            tcds: Tcds,
                            message_builder: asrt.MessageBuilder):
        pass
