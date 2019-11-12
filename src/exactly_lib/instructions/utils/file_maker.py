from typing import Sequence, Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.data.path_resolver import PathResolver
from exactly_lib.symbol.logic.program.program_resolver import ProgramResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator, ConstantSuccessValidator, \
    ValidationStep
from exactly_lib.test_case_utils import path_check, file_properties, file_creation
from exactly_lib.test_case_utils.file_creation import create_file_from_transformation_of_existing_file__dp
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
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
             dst_file: DescribedPathPrimitive,
             ) -> Optional[TextRenderer]:
        """
        :param dst_file: The path to create - fails if already exists etc
        :return: Error message, in case of error, else None
        """
        raise NotImplementedError('abstract method')


class FileMakerForConstantContents(FileMaker):
    def __init__(self, contents: string_resolver.StringResolver):
        self._contents = contents

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: DescribedPathPrimitive,
             ) -> Optional[TextRenderer]:
        contents_str = self._contents.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)

        return _create_file(dst_path, contents_str)

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
             dst_path: DescribedPathPrimitive,
             ) -> Optional[TextRenderer]:
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
            return text_docs.single_pre_formatted_line_object(err_msg)

        path_of_output = storage_dir / result_and_std_err.result.file_names.name_of(self._output_channel)
        return create_file_from_transformation_of_existing_file__dp(path_of_output,
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
                 src_path: PathResolver):
        self._source_info = source_info
        self._transformer = transformer
        self._src_path = src_path

        self._src_file_validator = path_check.PathCheckValidator(
            path_check.PathCheck(src_path,
                                    file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                                      follow_symlinks=True)))

        self._validator = pre_or_post_validation.AndValidator([
            pre_or_post_validation.SingleStepValidator(ValidationStep.PRE_SDS,
                                                       self._src_file_validator),
            pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(
                lambda symbols: self._transformer.resolve(symbols).validator(),
            )
        ])

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return tuple(self._transformer.references) + tuple(self._src_path.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: DescribedPathPrimitive,
             ) -> Optional[TextRenderer]:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        src_validation_res = self._src_file_validator.validate_post_sds_if_applicable(path_resolving_env)
        if src_validation_res:
            return src_validation_res

        transformer = self._transformer \
            .resolve(path_resolving_env.symbols) \
            .value_of_any_dependency(path_resolving_env.home_and_sds)
        src_path = self._src_path.resolve_value_of_any_dependency(path_resolving_env)

        return create_file_from_transformation_of_existing_file__dp(src_path,
                                                                    dst_path,
                                                                    transformer)


def _create_file(path_to_create: DescribedPathPrimitive,
                 contents_str: str) -> Optional[TextRenderer]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def write_file(f):
        f.write(contents_str)

    return file_creation.create_file__dp(path_to_create,
                                         write_file)
