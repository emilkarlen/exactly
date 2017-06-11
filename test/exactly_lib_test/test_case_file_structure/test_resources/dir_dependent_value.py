import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_dir_dependent_value(expected: DirDependentValue) -> asrt.ValueAssertion:
    return DirDependentValueAssertion(expected)


class DirDependentValueAssertion(asrt.ValueAssertion):
    def __init__(self, expected: DirDependentValue):
        self._expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, DirDependentValue,
                             'Actual value is expected to be a ' + str(DirDependentValue))
        assert isinstance(value, DirDependentValue)

        self._check_existence(put, value, message_builder)
        self._check_dir_dependency(put, value, message_builder)

        home_and_sds = dummy_home_and_sds()
        self._check_value(put, value, home_and_sds, message_builder)

        self._check_custom(put, value, home_and_sds, message_builder)

    def _check_custom(self,
                      put: unittest.TestCase,
                      actual: DirDependentValue,
                      home_and_sds: HomeAndSds,
                      message_builder: asrt.MessageBuilder):
        pass

    def _check_existence(self,
                         put: unittest.TestCase,
                         actual: DirDependentValue,
                         message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.exists_pre_sds(),
                        actual.exists_pre_sds(),
                        message_builder.apply('exists_pre_sds'))

    def _check_dir_dependency(self,
                              put: unittest.TestCase,
                              actual: DirDependentValue,
                              message_builder: asrt.MessageBuilder):
        put.assertEqual(self._expected.has_dir_dependency(),
                        actual.has_dir_dependency(),
                        message_builder.apply('has_dir_dependency'))

    def _check_value(self,
                     put: unittest.TestCase,
                     actual: DirDependentValue,

                     home_and_sds: HomeAndSds,
                     message_builder: asrt.MessageBuilder):
        if self._expected.exists_pre_sds():
            put.assertEqual(self._expected.value_pre_sds(home_and_sds.home_dir_path),
                            actual.value_pre_sds(home_and_sds.home_dir_path),
                            message_builder.apply('value_pre_sds'))
        else:
            put.assertEqual(self._expected.value_post_sds(home_and_sds.sds),
                            actual.value_post_sds(home_and_sds.sds),
                            message_builder.apply('value_post_sds'))

        put.assertEqual(self._expected.value_pre_or_post_sds(home_and_sds),
                        actual.value_pre_or_post_sds(home_and_sds),
                        message_builder.apply('value_pre_or_post_sds'))
