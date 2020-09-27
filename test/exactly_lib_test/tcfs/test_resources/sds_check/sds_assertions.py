import unittest

from exactly_lib.tcfs.sds import SandboxDs, \
    RESULT_FILE__EXITCODE
from exactly_lib_test.test_resources.files.file_checks import FileChecker, file_does_not_exist
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertion, \
    ValueAssertionBase


def is_sandbox_directory_structure_after_execution(fc: FileChecker,
                                                   root_dir_name: str):
    sds = SandboxDs(root_dir_name)
    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                          len(sds.all_root_dirs__including_result()))
    for d in sds.all_leaf_dirs__including_result():
        fc.assert_exists_dir(d)

    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.result.root_dir,
                                                          len(sds.result.all_files))
    for f in sds.result.all_files:
        fc.assert_exists_plain_file(f)


def is_sds_root_dir() -> ValueAssertion[str]:
    return _IsSdsRootDir()


class _IsSdsRootDir(ValueAssertionBase[str]):
    def _apply(self,
               put: unittest.TestCase,
               value: str,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, str)

        fc = FileChecker(put, message_builder.apply(''))
        sds = SandboxDs(value)

        fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                              len(sds.all_root_dirs__including_result()))
        for d in sds.all_leaf_dirs__including_result():
            fc.assert_exists_dir(d)


def sds_root_dir_exists_and_has_sds_dirs() -> ValueAssertion[SandboxDs]:
    return asrt.on_transformed(lambda sds: str(sds.root_dir),
                               is_sds_root_dir())


def sds_root_dir_does_not_exist() -> ValueAssertion[SandboxDs]:
    return asrt.on_transformed(lambda sds: sds.root_dir,
                               file_does_not_exist())


def is_existing_sds_with_post_execution_files() -> ValueAssertion[SandboxDs]:
    return _SdsRootDirExistsAndContainsPostExecutionFiles()


def is_existing_sds_with_post_execution_w_only_exitcode_result_files(exit_code: int) \
        -> ValueAssertion[SandboxDs]:
    return asrt.and_([
        sds_root_dir_exists_and_has_sds_dirs(),
        asrt.sub_component('result-dir',
                           SandboxDs.result_dir.fget,
                           DirContainsExactly(DirContents([
                               File(RESULT_FILE__EXITCODE, str(exit_code))
                           ])))
    ])


class _SdsRootDirExistsAndContainsPostExecutionFiles(ValueAssertionBase[SandboxDs]):
    def _apply(self,
               put: unittest.TestCase,
               value: SandboxDs,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, SandboxDs)

        fc = FileChecker(put, message_builder.apply(''))

        is_sandbox_directory_structure_after_execution(fc, str(value.root_dir))


class _SdsRootDirExistsAndContainsPostExecutionWOnlyExitCodeResultFiles(ValueAssertionBase[SandboxDs]):
    def _apply(self,
               put: unittest.TestCase,
               value: SandboxDs,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, SandboxDs)

        fc = FileChecker(put, message_builder.apply(''))

        is_sandbox_directory_structure_after_execution(fc, str(value.root_dir))
