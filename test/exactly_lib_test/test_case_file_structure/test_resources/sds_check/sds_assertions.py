import unittest

from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib_test.test_resources.file_checks import FileChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def is_sandbox_directory_structure_after_execution(fc: FileChecker,
                                                   root_dir_name: str):
    sds = sandbox_directory_structure.SandboxDirectoryStructure(root_dir_name)
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
        sds = sandbox_directory_structure.SandboxDirectoryStructure(value)

        fc.assert_exists_dir_with_given_number_of_files_in_it(sds.root_dir,
                                                              5)
        fc.assert_exists_dir(sds.test_case_dir)
        fc.assert_exists_dir(sds.tmp.root_dir)
        fc.assert_exists_dir(sds.tmp.internal_dir)
        fc.assert_exists_dir(sds.tmp.user_dir)
        fc.assert_exists_dir(sds.act_dir)

        fc.assert_exists_dir(sds.log_dir)
