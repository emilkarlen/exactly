import os
import pathlib

from exactly_lib.execution import environment_variables
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util import file_utils
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActEnvironment, \
    ActResultProducer
from exactly_lib_test.test_resources.execution.utils import ActResult


class ReplacedEnvVarsFileContentsConstructor:
    def __init__(self):
        self.sorted_env_var_keys = sorted(environment_variables.ALL_REPLACED_ENV_VARS)

    def contents_before_replacement(self, home_and_sds: HomeAndSds) -> str:
        env_vars_dict = environment_variables.replaced(home_and_sds.home_dir_path,
                                                       home_and_sds.sds)
        values_in_determined_order = list(map(env_vars_dict.get, self.sorted_env_var_keys))
        return self.content_from_values(values_in_determined_order,
                                        home_and_sds)

    def expected_contents_after_replacement(self, home_and_sds: HomeAndSds) -> str:
        return self.content_from_values(self.sorted_env_var_keys,
                                        home_and_sds)

    def unexpected_contents_after_replacement(self, home_and_sds: HomeAndSds) -> str:
        """
        :return: Gives a variation of the expected result, that is not equal to the expected result.
        """
        return self.content_from_values(tuple(reversed(self.sorted_env_var_keys)),
                                        home_and_sds)

    @staticmethod
    def content_from_values(values_in_determined_order: iter,
                            home_and_sds: HomeAndSds) -> str:
        """
        Generates a string with a combination of values that should, and should not, be replaced.
        """
        all_values_concatenated = ''.join(values_in_determined_order)
        all_values_on_separate_lines = os.linesep.join(values_in_determined_order)
        all_values_concatenated_in_reverse_order = ''.join(reversed(values_in_determined_order))
        sds = home_and_sds.sds
        should_not_be_replaced_values = os.linesep.join([str(sds.root_dir),
                                                         str(sds.result.root_dir)])
        return os.linesep.join([all_values_concatenated,
                                all_values_on_separate_lines,
                                all_values_concatenated_in_reverse_order,
                                should_not_be_replaced_values]) + os.linesep


class FileWriter:
    def __init__(self,
                 file_name: str):
        self.file_name = file_name

    def write(self,
              act_environment: ActEnvironment,
              contents: str):
        file_path = self._get_directory(act_environment) / self.file_name
        file_utils.write_new_text_file(file_path, contents)

    def _get_directory(self, act_environment: ActEnvironment) -> pathlib.Path:
        raise NotImplementedError()


class ActResultContentsSetup:
    def result_for(self, contents: str) -> ActResult:
        raise NotImplementedError()


class ActResultProducerForContentsWithAllReplacedEnvVars(ActResultProducer):
    def __init__(self,
                 act_result_contents_setup: ActResultContentsSetup,
                 source_file_writer: FileWriter,
                 source_should_contain_expected_value: bool):
        self._act_result_contents_setup = act_result_contents_setup
        self._source_file_writer = source_file_writer
        self._source_should_contain_expected_value = source_should_contain_expected_value
        self._contents_constructor = ReplacedEnvVarsFileContentsConstructor()

    def apply(self, act_environment: ActEnvironment) -> ActResult:
        self._write_source_file(act_environment)
        contents = self._contents_constructor.contents_before_replacement(act_environment.home_and_sds)
        return self._act_result_contents_setup.result_for(contents)

    def _write_source_file(self, act_environment: ActEnvironment):
        if self._source_should_contain_expected_value:
            contents = self._contents_constructor.expected_contents_after_replacement(act_environment.home_and_sds)
        else:
            contents = self._contents_constructor.unexpected_contents_after_replacement(act_environment.home_and_sds)
        self._source_file_writer.write(act_environment, contents)


class WriteFileToHomeDir(FileWriter):
    def _get_directory(self, act_environment: ActEnvironment) -> pathlib.Path:
        return act_environment.home_and_sds.home_dir_path


class WriteFileToCurrentDir(FileWriter):
    def _get_directory(self, act_environment: ActEnvironment) -> pathlib.Path:
        return pathlib.Path.cwd()


class StoreContentsInFileInCurrentDir(ActResultContentsSetup):
    def __init__(self,
                 file_name: str):
        self._file_name = file_name

    def result_for(self, contents: str) -> ActResult:
        file_path = pathlib.Path.cwd() / self._file_name
        file_utils.write_new_text_file(file_path, contents)
        return ActResult()


class StoreContentsInFileInParentDirOfCwd(ActResultContentsSetup):
    def __init__(self,
                 file_name: str):
        self._file_name = file_name

    def result_for(self, contents: str) -> ActResult:
        file_path = pathlib.Path.cwd().parent / self._file_name
        file_utils.write_new_text_file(file_path, contents)
        return ActResult()


class OutputContentsToStdout(ActResultContentsSetup):
    def result_for(self, contents: str) -> ActResult:
        return ActResult(stdout_contents=contents)


class OutputContentsToStderr(ActResultContentsSetup):
    def result_for(self, contents: str) -> ActResult:
        return ActResult(stderr_contents=contents)
