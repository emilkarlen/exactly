import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part
from exactly_lib_test.test_case_file_structure.test_resources.path_relativity import equals_path_relativity
from exactly_lib_test.test_case_file_structure.test_resources.paths import dummy_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_file_ref(expected: FileRef) -> asrt.ValueAssertion:
    return _AssertFileRefHasSpecifiedProperties(expected)


class _AssertFileRefHasSpecifiedProperties(asrt.ValueAssertion):
    def __init__(self, expected: FileRef):
        self._expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, FileRef,
                             'Actual value is expected to be a ' + str(FileRef))
        assert isinstance(value, FileRef)

        home_and_sds = dummy_home_and_sds()

        self._check_path_suffix(put,
                                value,
                                message_builder.for_sub_component('path_suffix'))

        self._check_relativity(put, value, message_builder)

        self._check_exists_pre_sds(put, value, message_builder)

        self._check_paths(put, value, message_builder, home_and_sds)

    def _check_path_suffix(self,
                           put: unittest.TestCase,
                           actual: FileRef,
                           message_builder: asrt.MessageBuilder):
        path_suffix = self._expected.path_suffix()
        equals_path_part(path_suffix).apply(put,
                                            actual.path_suffix(),
                                            message_builder)

    def _check_symbol_references(self,
                                 put: unittest.TestCase,
                                 message_builder: asrt.MessageBuilder,
                                 actual: list):
        raise NotImplementedError()

    def _check_exists_pre_sds(self,
                              put: unittest.TestCase,
                              actual: FileRef,
                              message_builder: asrt.MessageBuilder):
        expected_exists_pre_sds = self._expected.exists_pre_sds()
        put.assertEqual(expected_exists_pre_sds,
                        actual.exists_pre_sds(),
                        message_builder.apply('exists_pre_sds'))

    def _check_paths(self,
                     put: unittest.TestCase,
                     actual: FileRef,
                     message_builder: asrt.MessageBuilder,
                     home_and_sds: HomeAndSds):
        expected_exists_pre_sds = self._expected.exists_pre_sds()
        if expected_exists_pre_sds:
            put.assertEqual(self._expected.file_path_pre_sds(home_and_sds.home_dir_path),
                            actual.file_path_pre_sds(home_and_sds.home_dir_path),
                            message_builder.apply('file_path_pre_sds'))
        else:
            put.assertEqual(self._expected.file_path_post_sds(home_and_sds.sds),
                            actual.file_path_post_sds(home_and_sds.sds),
                            message_builder.apply('file_path_post_sds'))

    def _check_relativity(self,
                          put: unittest.TestCase,
                          actual_file_ref: FileRef,
                          message_builder: asrt.MessageBuilder):
        expected = self._expected.relativity()
        actual = actual_file_ref.relativity()
        assertion = equals_path_relativity(expected)
        assertion.apply(put, actual, message_builder.for_sub_component('specific_relativity'))
