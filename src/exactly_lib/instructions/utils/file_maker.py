from typing import Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.data import string_sdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.sdv_validation import SdvValidator, ConstantSuccessSdvValidator, \
    ValidationStep
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, InstructionSourceInfo, \
    instruction_log_dir
from exactly_lib.test_case_utils import path_check, file_properties, file_creation
from exactly_lib.test_case_utils.file_creation import FileTransformerHelper
from exactly_lib.test_case_utils.program import top_lvl_error_msg_rendering
from exactly_lib.test_case_utils.program_execution import exe_wo_transformation
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


class FileMaker:
    """
    Makes a file with a given path.

    Lets sub classes determine the contents of the file.
    """

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> SdvValidator:
        return ConstantSuccessSdvValidator()

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_file: DescribedPath,
             ) -> Optional[TextRenderer]:
        """
        :param dst_file: The path to create - fails if already exists etc
        :return: Error message, in case of error, else None
        """
        raise NotImplementedError('abstract method')


class FileMakerForConstantContents(FileMaker):
    def __init__(self, contents: string_sdv.StringSdv):
        self._contents = contents

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: DescribedPath,
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
                 program: ProgramSdv):
        self._output_channel = output_channel
        self._source_info = source_info
        self._program = program

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: DescribedPath,
             ) -> Optional[TextRenderer]:
        resolver = resolving_helper_for_instruction_env(os_services, environment)
        program = resolver.resolve_program(self._program)
        storage_dir = instruction_log_dir(environment.phase_logging, self._source_info)

        try:
            result = exe_wo_transformation.execute(
                program,
                storage_dir,
                os_services,
                environment.process_execution_settings,
                file_ctx_managers.dev_null()
            )
        except HardErrorException as ex:
            return ex.error

        if result.exit_code != 0:
            return top_lvl_error_msg_rendering.non_zero_exit_code_msg(program.structure(),
                                                                      result.exit_code,
                                                                      result.stderr_contents)

        transformation_helper = FileTransformerHelper(
            os_services,
            environment.tmp_file_space,
        )
        src_path = storage_dir / result.file_names.name_of(self._output_channel)
        return transformation_helper.transform_to_file__dp(src_path,
                                                           dst_path,
                                                           program.transformation)

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.SdvValidatorFromDdvValidator(
            lambda symbols: self._program.resolve(symbols).validator
        )

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return self._program.references


class FileMakerForContentsFromExistingFile(FileMaker):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 transformer: StringTransformerSdv,
                 src_path: PathSdv):
        self._source_info = source_info
        self._transformer = transformer
        self._src_path = src_path

        self._src_file_validator = path_check.PathCheckValidator(
            path_check.PathCheck(src_path,
                                 file_properties.must_exist_as(file_properties.FileType.REGULAR,
                                                               follow_symlinks=True)))

        self._validator = sdv_validation.AndSdvValidator([
            sdv_validation.SingleStepSdvValidator(ValidationStep.PRE_SDS,
                                                  self._src_file_validator),
            sdv_validation.SdvValidatorFromDdvValidator(
                lambda symbols: self._transformer.resolve(symbols).validator,
            )
        ])

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return tuple(self._transformer.references) + tuple(self._src_path.references)

    @property
    def validator(self) -> SdvValidator:
        return self._validator

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_path: DescribedPath,
             ) -> Optional[TextRenderer]:
        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        src_validation_res = self._src_file_validator.validate_post_sds_if_applicable(path_resolving_env)
        if src_validation_res:
            return src_validation_res

        resolver = resolving_helper_for_instruction_env(os_services, environment)
        transformer = resolver.resolve_string_transformer(self._transformer)
        src_path = self._src_path.resolve_value_of_any_dependency(path_resolving_env)

        transformation_helper = FileTransformerHelper(
            os_services,
            environment.tmp_file_space,
        )
        return transformation_helper.transform_to_file__dp(src_path,
                                                           dst_path,
                                                           transformer)


def _create_file(path_to_create: DescribedPath,
                 contents_str: str) -> Optional[TextRenderer]:
    """
    :return: None iff success. Otherwise an error message.
    """

    def write_file(f):
        f.write(contents_str)

    return file_creation.create_file__dp(path_to_create,
                                         write_file)
