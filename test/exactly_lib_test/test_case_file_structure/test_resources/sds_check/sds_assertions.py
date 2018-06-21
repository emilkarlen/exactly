import unittest

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure, \
    RESULT_FILE__EXITCODE
from exactly_lib_test.test_resources.files.file_checks import FileChecker
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.file_assertions import DirContainsExactly
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def is_sandbox_directory_structure_after_execution(fc: FileChecker,
                                                   root_dir_name: str):
    sds = SandboxDirectoryStructure(root_dir_name)
    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                          5)
    fc.assert_exists_dir(sds.test_case_dir)
    fc.assert_exists_dir(sds.tmp.root_dir)
    fc.assert_exists_dir(sds.tmp.internal_dir)
    fc.assert_exists_dir(sds.tmp.user_dir)
    fc.assert_exists_dir(sds.act_dir)

    fc.assert_exists_dir_with_given_number_of_files_in_it(sds.result.root_dir,
                                                          3)
    fc.assert_exists_plain_file(sds.result.exitcode_file)
    fc.assert_exists_plain_file(sds.result.stdout_file)
    fc.assert_exists_plain_file(sds.result.stderr_file)

    fc.assert_exists_dir(sds.log_dir)


def is_sds_root_dir() -> asrt.ValueAssertion[str]:
    return _IsSdsRootDir()


class _IsSdsRootDir(asrt.ValueAssertion[str]):
    def apply(self,
              put: unittest.TestCase,
              value: str,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, str)

        fc = FileChecker(put, message_builder.apply(''))
        sds = SandboxDirectoryStructure(value)

        fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                              5)
        fc.assert_exists_dir(sds.test_case_dir)
        fc.assert_exists_dir(sds.tmp.root_dir)
        fc.assert_exists_dir(sds.tmp.internal_dir)
        fc.assert_exists_dir(sds.tmp.user_dir)
        fc.assert_exists_dir(sds.act_dir)

        fc.assert_exists_dir(sds.log_dir)


def sds_root_dir_exists_and_has_sds_dirs() -> asrt.ValueAssertion[SandboxDirectoryStructure]:
    return asrt.on_transformed(lambda sds: str(sds.root_dir),
                               is_sds_root_dir())


def is_existing_sds_with_post_execution_files() -> asrt.ValueAssertion[SandboxDirectoryStructure]:
    return _SdsRootDirExistsAndContainsPostExecutionFiles()


def is_existing_sds_with_post_execution_w_only_exitcode_result_files(exit_code: int) \
        -> asrt.ValueAssertion[SandboxDirectoryStructure]:
    return asrt.and_([
        sds_root_dir_exists_and_has_sds_dirs(),
        asrt.sub_component('result-dir',
                           lambda sds: sds.result.root_dir,
                           DirContainsExactly(DirContents([
                               File(RESULT_FILE__EXITCODE, str(exit_code))
                           ])))
    ])


class _SdsRootDirExistsAndContainsPostExecutionFiles(asrt.ValueAssertion[SandboxDirectoryStructure]):
    def apply(self,
              put: unittest.TestCase,
              value: SandboxDirectoryStructure,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, SandboxDirectoryStructure)

        fc = FileChecker(put, message_builder.apply(''))

        is_sandbox_directory_structure_after_execution(fc, str(value.root_dir))


class _SdsRootDirExistsAndContainsPostExecutionWOnlyExitCodeResultFiles(asrt.ValueAssertion[SandboxDirectoryStructure]):
    def apply(self,
              put: unittest.TestCase,
              value: SandboxDirectoryStructure,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, SandboxDirectoryStructure)

        fc = FileChecker(put, message_builder.apply(''))

        is_sandbox_directory_structure_after_execution(fc, str(value.root_dir))
