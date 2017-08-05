import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue, SingleDirDependentValue, \
    MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_single_dir_dependent_value(expected: SingleDirDependentValue) -> asrt.ValueAssertion:
    return SingleDirDependentValueAssertion(SingleDirDependentValue, expected)


def equals_multi_dir_dependent_value(expected: MultiDirDependentValue) -> asrt.ValueAssertion:
    return MultiDirDependentValueAssertion(MultiDirDependentValue, expected)


class DirDependentValueAssertionBase(asrt.ValueAssertion):
    def __init__(self,
                 expected_type,
                 expected: DirDependentValue):
        self._expected_type = expected_type
        self._expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        self._check_type(put, value, message_builder)
        assert isinstance(value, DirDependentValue)

        self._check_common_dependencies(put, value, message_builder)
        self._check_existence(put, value, message_builder)

        home_and_sds = dummy_home_and_sds()
        self._check_custom_dependencies(put, value, home_and_sds, message_builder)
        self._check_value(put, value, home_and_sds, message_builder)

        self._check_custom(put, value, home_and_sds, message_builder)

    def _check_type(self,
                    put: unittest.TestCase,
                    actual,
                    message_builder: asrt.MessageBuilder
                    ):
        put.assertIsInstance(actual, self._expected_type,
                             message_builder.apply('Actual value is expected to be a ' + str(self._expected_type)))

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: DirDependentValue,
                                   home_and_sds: HomeAndSds,
                                   message_builder: asrt.MessageBuilder):
        raise NotImplementedError()

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: DirDependentValue,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        raise NotImplementedError()

    def _check_existence(self,
                         put: unittest.TestCase,
                         actual: DirDependentValue,
                         message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.exists_pre_sds(),
                        actual.exists_pre_sds(),
                        message_builder.apply('exists_pre_sds'))

    def _check_common_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: DirDependentValue,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.has_dir_dependency(),
                        actual.has_dir_dependency(),
                        message_builder.apply('has_dir_dependency'))
        put.assertEqual(self._expected.resolving_dependencies(),
                        actual.resolving_dependencies(),
                        message_builder.apply('resolving_dependencies'))

    def _check_value(self,
                     put: unittest.TestCase,
                     actual: DirDependentValue,
                     home_and_sds: HomeAndSds,
                     message_builder: asrt.MessageBuilder):
        if not self._expected.has_dir_dependency():
            put.assertEqual(self._expected.value_when_no_dir_dependencies(),
                            actual.value_when_no_dir_dependencies(),
                            message_builder.apply('value_when_no_dir_dependencies'))

        put.assertEqual(self._expected.value_of_any_dependency(home_and_sds),
                        actual.value_of_any_dependency(home_and_sds),
                        message_builder.apply('value_of_any_dependency'))


class SingleDirDependentValueAssertion(DirDependentValueAssertionBase):
    def __init__(self, expected_type, expected: SingleDirDependentValue):
        super().__init__(expected_type, expected)
        self._expected_single_dep_value = expected

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: SingleDirDependentValue,
                                   home_and_sds: HomeAndSds,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_single_dep_value.resolving_dependency(),
                        actual.resolving_dependency(),
                        message_builder.apply('resolving_dependency'))

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: SingleDirDependentValue,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        if self._expected.exists_pre_sds():
            put.assertEqual(self._expected_single_dep_value.value_pre_sds_hds(home_and_sds.hds),
                            actual.value_pre_sds_hds(home_and_sds.hds),
                            message_builder.apply('value_pre_sds_hds'))
        else:
            put.assertEqual(self._expected_single_dep_value.value_post_sds(home_and_sds.sds),
                            actual.value_post_sds(home_and_sds.sds),
                            message_builder.apply('value_post_sds'))
        self._check_custom_single(put, actual, home_and_sds, message_builder)

    def _check_custom_single(self,
                             put: unittest.TestCase,
                             actual: SingleDirDependentValue,
                             home_and_sds: HomeAndSds,
                             message_builder: asrt.MessageBuilder):
        pass


class MultiDirDependentValueAssertion(DirDependentValueAssertionBase):
    def __init__(self, expected_type, expected: MultiDirDependentValue):
        super().__init__(expected_type, expected)
        self._expected_multi_dep_value = expected

    def _check_custom_dependencies(self,
                                   put: unittest.TestCase,
                                   actual: MultiDirDependentValue,
                                   home_and_sds: HomeAndSds,
                                   message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_multi_dep_value.dir_dependency(),
                        actual.dir_dependency(),
                        message_builder.apply('dir_dependency'))

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: MultiDirDependentValue,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected_multi_dep_value.dir_dependency(),
                        actual.dir_dependency(),
                        'dir_dependency')

        self._check_custom_multi(put, actual, home_and_sds, message_builder)

    def _check_custom_multi(self,
                            put: unittest.TestCase,
                            actual: MultiDirDependentValue,
                            home_and_sds: HomeAndSds,
                            message_builder: asrt.MessageBuilder):
        pass
