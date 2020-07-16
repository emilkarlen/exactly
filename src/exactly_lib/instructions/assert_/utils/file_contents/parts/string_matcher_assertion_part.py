from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import rendering__node_bool
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import pfh_exception
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv, StringMatcher
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.render import combinators as rend_comb


class StringMatcherAssertionPart(FileContentsAssertionPart):
    def __init__(self, string_matcher: StringMatcherSdv):
        super().__init__(sdv_validation.SdvValidatorFromDdvValidator(
            lambda symbols: string_matcher.resolve(symbols).validator
        ))
        self._string_matcher = string_matcher

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string_matcher.references

    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               os_services: OsServices,
               model: StringModel):
        resolver = resolving_helper_for_instruction_env(os_services, environment)
        string_matcher = resolver.resolve_matcher(self._string_matcher)

        matching_result = self._apply_matcher(string_matcher, model)

        if not matching_result.value:
            raise pfh_exception.PfhFailException(
                rend_comb.SingletonSequenceR(
                    rendering__node_bool.BoolTraceRenderer(matching_result.trace))
            )

    @staticmethod
    def _apply_matcher(matcher: StringMatcher,
                       model: StringModel,
                       ) -> MatchingResult:
        try:
            return matcher.matches_w_trace(model)
        except HardErrorException as ex:
            raise pfh_exception.PfhHardErrorException(ex.error)
