from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.path_description import PathValuePartConstructor
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.util.logic_types import ExpectationType


class Settings:
    def __init__(self,
                 expectation_type: ExpectationType,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        self.expectation_type = expectation_type
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher


class _InstructionBase(AssertPhaseInstruction):
    def __init__(self, settings: Settings):
        self.settings = settings

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return pfh_ex_method.translate_pfh_exception_to_pfh(self.__main_that_reports_result_via_exceptions,
                                                            environment, os_services)

    def _property_descriptor(self, property_name: str) -> property_description.PropertyDescriptor:
        return property_description.PropertyDescriptorWithConstantPropertyName(
            property_name,
            property_description.multiple_object_descriptors([
                PathValuePartConstructor(self.settings.path_to_check),
                parse_file_matcher.SelectorsDescriptor(self.settings.file_matcher),
            ])
        )

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        raise NotImplementedError('abstract method')

    def __main_that_reports_result_via_exceptions(self, environment: InstructionEnvironmentForPostSdsStep,
                                                  os_services: OsServices):
        assertion = AssertPathIsExistingDirectory()
        assertion.check(environment, os_services, self.settings)
        self._main_after_checking_existence_of_dir(environment)


class AssertPathIsExistingDirectory(AssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: Settings) -> Settings:
        expect_existing_dir = file_properties.must_exist_as(file_properties.FileType.DIRECTORY,
                                                            True)

        path_resolving_env = environment.path_resolving_environment_pre_or_post_sds
        failure_message = file_ref_check.pre_or_post_sds_failure_message_or_none(
            file_ref_check.FileRefCheck(settings.path_to_check,
                                        expect_existing_dir),
            path_resolving_env)
        if failure_message is not None:
            raise pfh_ex_method.PfhFailException(failure_message)
        else:
            return settings
