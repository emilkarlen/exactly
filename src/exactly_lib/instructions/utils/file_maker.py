import pathlib

from exactly_lib.instructions.utils import file_creation
from exactly_lib.instructions.utils.file_creation import create_file_from_transformation_of_existing_file
from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils import file_ref_check, file_properties
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator, ConstantSuccessValidator, \
    SingleStepValidator, ValidationStep
from exactly_lib.test_case_utils.sub_proc.execution_setup import SubProcessExecutionSetup
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import ExecutorThatStoresResultInFilesInDir, \
    execute_and_read_stderr_if_non_zero_exitcode, result_for_non_success_or_non_zero_exit_code


class FileMaker:
    """
    Makes a file with a given path.

    Lets sub classes determine the contents of the file.
    """

    @property
    def symbol_references(self) -> list:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return ConstantSuccessValidator()

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             dst_file: pathlib.Path,
             ) -> str:
        """
        :param dst_file: The path of a (probably!) non-existing file
        :return: Error message, in case of error, else None
        """
        raise NotImplementedError('abstract method')


class FileMakerForConstantContents(FileMaker):
    def __init__(self, contents: string_resolver.StringResolver):
        self._contents = contents

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             dst_path: pathlib.Path,
             ) -> str:
        contents_str = self._contents.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)

        return create_file(dst_path, contents_str)

    @property
    def symbol_references(self) -> list:
        return self._contents.references


class FileMakerForContentsFromSubProcess(FileMaker):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 output_transformer: LinesTransformerResolver,
                 sub_process: SubProcessExecutionSetup):
        self._source_info = source_info
        self._output_transformer = output_transformer
        self._sub_process = sub_process

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             dst_path: pathlib.Path,
             ) -> str:
        executor = ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        command = self._sub_process.resolve_command(path_resolving_env)
        storage_dir = instruction_log_dir(environment.phase_logging, self._source_info)

        result_and_std_err = execute_and_read_stderr_if_non_zero_exitcode(command, executor, storage_dir)

        err_msg = result_for_non_success_or_non_zero_exit_code(result_and_std_err)
        if err_msg:
            return err_msg

        path_of_output = storage_dir / result_and_std_err.result.file_names.stdout
        transformer = self._output_transformer.resolve(path_resolving_env.symbols)

        return create_file_from_transformation_of_existing_file(path_of_output,
                                                                dst_path,
                                                                transformer,
                                                                path_resolving_env.home_and_sds)

    @property
    def symbol_references(self) -> list:
        return (self._output_transformer.references +
                self._sub_process.symbol_usages)


class FileMakerForContentsFromExistingFile(FileMaker):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 transformer: LinesTransformerResolver,
                 src_path: FileRefResolver):
        self._source_info = source_info
        self._transformer = transformer
        self._src_path = src_path

        self._src_file_validator = file_ref_check.FileRefCheckValidator(
            file_ref_check.FileRefCheck(src_path,
                                        file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                      follow_symlinks=True)))

    @property
    def symbol_references(self) -> list:
        return self._transformer.references + self._src_path.references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return SingleStepValidator(ValidationStep.PRE_SDS,
                                   self._src_file_validator)

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             dst_path: pathlib.Path,
             ) -> str:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        src_validation_res = self._src_file_validator.validate_post_sds_if_applicable(path_resolving_env)
        if src_validation_res:
            return src_validation_res

        transformer = self._transformer.resolve(path_resolving_env.symbols)
        src_path = self._src_path.resolve_value_of_any_dependency(path_resolving_env)

        return create_file_from_transformation_of_existing_file(src_path,
                                                                dst_path,
                                                                transformer,
                                                                path_resolving_env.home_and_sds)


def create_file(path_to_create: pathlib.Path,
                contents_str: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """

    def write_file(f):
        f.write(contents_str)

    return file_creation.create_file(path_to_create,
                                     write_file)
