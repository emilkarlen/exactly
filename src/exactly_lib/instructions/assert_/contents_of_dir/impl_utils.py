from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, Environment
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties, return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException, PfhHardErrorException
from exactly_lib.type_system.logic.hard_error import HardErrorException


class FilesSource:
    def __init__(self,
                 path_of_dir: FileRefResolver):
        self._path_of_dir = path_of_dir

    @property
    def path_of_dir(self) -> FileRefResolver:
        return self._path_of_dir


class AssertPathIsExistingDirectory(AssertionPart[FilesSource, FilesSource]):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        failure_message = file_ref_check.pre_or_post_sds_failure_message_or_none(
            file_ref_check.FileRefCheck(files_source.path_of_dir,
                                        expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)
        else:
            return files_source


class FilesMatcherAsDirContentsAssertionPart(AssertionPart[FilesSource, FilesSource]):
    def __init__(self, files_matcher: FilesMatcherResolver):
        super().__init__(files_matcher.validator())
        self._files_matcher = files_matcher

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._files_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:
        env = Environment(environment.path_resolving_environment_pre_or_post_sds,
                          environment.phase_logging.space_for_instruction())
        model = FilesMatcherModelForDir(files_source.path_of_dir,
                                        env.path_resolving_environment)
        value = self._files_matcher.resolve(environment.symbols)
        try:
            mb_error_message = value.matches(env,
                                             model)
            if mb_error_message is not None:
                raise PfhFailException(mb_error_message.resolve(err_msg_env_from_instr_env(environment)))

            return files_source
        except HardErrorException as ex:
            err_msg_env = err_msg_env_from_instr_env(environment)
            err_msg = ex.error.resolve(err_msg_env)
            raise PfhHardErrorException(err_msg)
