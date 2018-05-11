import pathlib
from typing import Sequence, Optional

from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator, ConstantSuccessValidator, \
    SingleStepValidator, ValidationStep
from exactly_lib.test_case_utils import file_ref_check, file_properties, file_creation
from exactly_lib.test_case_utils.file_creation import create_file_from_transformation_of_existing_file
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.process_execution.sub_process_execution import ExecutorThatStoresResultInFilesInDir, \
    execute_and_read_stderr_if_non_zero_exitcode, result_for_non_success_or_non_zero_exit_code


class FileMaker:
    """
    Makes a file with a given path.

    Lets sub classes determine the contents of the file.
    """

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return ConstantSuccessValidator()

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_file: pathlib.Path,
             ) -> Optional[str]:
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
             os_services: OsServices,
             dst_path: pathlib.Path,
             ) -> Optional[str]:
        contents_str = self._contents.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)

        return create_file(dst_path, contents_str)

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return self._contents.references


class FileMakerForContentsFromProgram(FileMaker):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 output_channel: ProcOutputFile,
                 program: ProgramResolver):
        self._output_channel = output_channel
        self._source_info = source_info
        self._program = program

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: pathlib.Path,
             ) -> Optional[str]:
        executor = ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds

        program = self._program \
            .resolve(path_resolving_env.symbols) \
            .value_of_any_dependency(path_resolving_env.home_and_sds)

        executable = os_services.executable_factory__detect_ex().make(program.command)
        storage_dir = instruction_log_dir(environment.phase_logging, self._source_info)

        result_and_std_err = execute_and_read_stderr_if_non_zero_exitcode(executable, executor, storage_dir)

        err_msg = result_for_non_success_or_non_zero_exit_code(result_and_std_err)
        if err_msg:
            return err_msg

        path_of_output = storage_dir / result_and_std_err.result.file_names.name_of(self._output_channel)
        return create_file_from_transformation_of_existing_file(path_of_output,
                                                                dst_path,
                                                                program.transformation)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._program.validator

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return self._program.references


class FileMakerForContentsFromExistingFile(FileMaker):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 transformer: StringTransformerResolver,
                 src_path: FileRefResolver):
        self._source_info = source_info
        self._transformer = transformer
        self._src_path = src_path

        self._src_file_validator = file_ref_check.FileRefCheckValidator(
            file_ref_check.FileRefCheck(src_path,
                                        file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                      follow_symlinks=True)))

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return tuple(self._transformer.references) + tuple(self._src_path.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return SingleStepValidator(ValidationStep.PRE_SDS,
                                   self._src_file_validator)

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: pathlib.Path,
             ) -> Optional[str]:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        src_validation_res = self._src_file_validator.validate_post_sds_if_applicable(path_resolving_env)
        if src_validation_res:
            return src_validation_res

        transformer = self._transformer \
            .resolve(path_resolving_env.symbols) \
            .value_of_any_dependency(path_resolving_env.home_and_sds)
        src_path = self._src_path.resolve_value_of_any_dependency(path_resolving_env)

        return create_file_from_transformation_of_existing_file(src_path,
                                                                dst_path,
                                                                transformer)


def create_file(path_to_create: pathlib.Path,
                contents_str: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """

    def write_file(f):
        f.write(contents_str)

    return file_creation.create_file(path_to_create,
                                     write_file)
