from typing import Sequence

from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart, \
    FileToCheck
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException


class StringMatcherAssertionPart(FileContentsAssertionPart):
    def __init__(self, string_matcher: StringMatcherResolver):
        super().__init__(string_matcher.validator)
        self._string_matcher = string_matcher

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string_matcher.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_check: FileToCheck) -> FileToCheck:
        value = self._string_matcher.resolve(environment.symbols)
        matcher = value.value_of_any_dependency(environment.home_and_sds)
        mb_error_message = matcher.matches(file_to_check)
        if mb_error_message is not None:
            raise PfhFailException(mb_error_message.resolve(err_msg_env_from_instr_env(environment)))
        return file_to_check
