from typing import Sequence, TypeVar, Generic

from exactly_lib.instructions.utils.logic_type_resolving_helper import resolving_helper_for_instruction_env
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case.result import svh
from exactly_lib.test_case_utils.description_tree import bool_trace_rendering
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock

T = TypeVar('T')


class Instruction(Generic[T], AssertPhaseInstruction):
    """Makes an instruction of a :class:`Matcher`"""

    def __init__(self,
                 matcher: MatcherSdv[None],
                 err_msg_header_renderer: Renderer[MajorBlock],
                 ):
        self._matcher = matcher
        self._err_msg_header_renderer = err_msg_header_renderer

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._matcher.references

    def validate_pre_sds(self,
                         environment: i.InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        validator = self._matcher.resolve(environment.symbols).validator
        err_msg = validator.validate_pre_sds_if_applicable(environment.hds)
        return svh.new_maybe_svh_validation_error(err_msg)

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        try:
            self._validate_post_setup(environment)
            return self._execute(environment)
        except HardErrorException as ex:
            return pfh.new_pfh_hard_error(ex.error)

    def _validate_post_setup(self, environment: i.InstructionEnvironmentForPostSdsStep):
        validator = self._matcher.resolve(environment.symbols).validator
        err_msg = validator.validate_post_sds_if_applicable(environment.tcds)
        if err_msg:
            raise HardErrorException(err_msg)

    def _execute(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pfh.PassOrFailOrHardError:
        result = resolving_helper_for_instruction_env(environment).apply(self._matcher, None)
        if result.value:
            return pfh.new_pfh_pass()
        else:
            err_msg = rend_comb.SequenceR([
                self._err_msg_header_renderer,
                bool_trace_rendering.BoolTraceRenderer(result.trace),
            ])
            return pfh.new_pfh_fail(err_msg)
