from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils import file_properties, return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher.files_matchers import Settings
from exactly_lib.test_case_utils.files_matcher.new_model_impl import FilesMatcherModelForDir
from exactly_lib.test_case_utils.files_matcher.structure import FilesSource, \
    FilesMatcherResolver, HardErrorException, Environment
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException, PfhHardErrorException


class DirContentsAssertionPart(AssertionPart[FilesSource, FilesSource]):
    def __init__(self,
                 settings: Settings,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        super().__init__(validator)
        self._settings = settings

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              files_source: FilesSource) -> FilesSource:
        raise NotImplementedError('abstract method')


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
                                        parse_file_matcher.CONSTANT_TRUE_MATCHER_RESOLVER,
                                        env.path_resolving_environment)
        try:
            mb_error_message = self._files_matcher.matches(env,
                                                           model)
            if mb_error_message is not None:
                raise PfhFailException(mb_error_message.resolve(err_msg_env_from_instr_env(environment)))

            return files_source
        except HardErrorException as ex:
            err_msg_env = err_msg_env_from_instr_env(environment)
            err_msg = ex.error.resolve(err_msg_env)
            raise PfhHardErrorException(err_msg)
