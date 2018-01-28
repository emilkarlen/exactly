from typing import Sequence

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as pfh_ex_method
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties, pre_or_post_validation
from exactly_lib.test_case_utils import file_ref_check
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.path_description import PathValuePartConstructor
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.logic_types import ExpectationType


class Settings:
    def __init__(self,
                 expectation_type: ExpectationType,
                 path_to_check: FileRefResolver,
                 file_matcher: FileMatcherResolver):
        self.expectation_type = expectation_type
        self.path_to_check = path_to_check
        self.file_matcher = file_matcher

    def property_descriptor(self, property_name: str) -> property_description.PropertyDescriptor:
        return property_description.PropertyDescriptorWithConstantPropertyName(
            property_name,
            property_description.multiple_object_descriptors([
                PathValuePartConstructor(self.path_to_check),
                parse_file_matcher.FileSelectionDescriptor(self.file_matcher),
            ])
        )


class DirContentsAssertionPart(AssertionPart):
    def __init__(self,
                 settings: Settings,
                 validator: PreOrPostSdsValidator = pre_or_post_validation.ConstantSuccessValidator()):
        super().__init__(validator)
        self._settings = settings

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: Settings) -> Settings:
        raise NotImplementedError('abstract method')


class AssertPathIsExistingDirectory(DirContentsAssertionPart):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._settings.path_to_check.references

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
