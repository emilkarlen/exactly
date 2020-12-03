from typing import Sequence

from exactly_lib.common.report_rendering.description_tree import rendering__node_bool
from exactly_lib.impls.exception import pfh_exception
from exactly_lib.impls.instructions.assert_.utils.file_contents.parts.file_assertion_part import \
    FileContentsAssertionPart
from exactly_lib.impls.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib.type_val_prims.string_source.string_source import StringSource
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
               model: StringSource):
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
                       model: StringSource,
                       ) -> MatchingResult:
        try:
            return matcher.matches_w_trace(model)
        except HardErrorException as ex:
            raise pfh_exception.PfhHardErrorException(ex.error)
