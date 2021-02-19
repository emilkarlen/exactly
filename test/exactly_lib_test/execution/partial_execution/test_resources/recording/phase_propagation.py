import enum
from typing import Optional, Dict

from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.util import functional


class PosInPhase(enum.Enum):
    BEFORE_MODIFY = 1
    AFTER_MODIFY = 2


class StepInfo(tuple):
    SOURCE__SETTINGS = 'vars-in-settings'
    SOURCE__ENVIRONMENT = 'vars-in-environment'

    def __new__(cls,
                phase: PhaseEnum,
                pos_in_phase: Optional[PosInPhase],
                source: str
                ):
        pos_in_phase_str = (
            '<no position>'
            if pos_in_phase is None
            else
            pos_in_phase.name
        )
        return tuple.__new__(cls, (phase.name, pos_in_phase_str, source))

    @staticmethod
    def of_settings(phase: PhaseEnum, pos_in_phase: Optional[PosInPhase]) -> 'StepInfo':
        return StepInfo(phase, pos_in_phase, StepInfo.SOURCE__SETTINGS)

    @staticmethod
    def of_environment(phase: PhaseEnum, pos_in_phase: Optional[PosInPhase]) -> 'StepInfo':
        return StepInfo(phase, pos_in_phase, StepInfo.SOURCE__ENVIRONMENT)


class RecordingEntry(tuple):
    def __new__(cls,
                step_info: StepInfo,
                environ: Optional[Dict[str, str]],
                timeout: Optional[int] = None,
                ):
        environ_to_record = functional.map_optional(dict, environ)
        return tuple.__new__(cls, (step_info, environ_to_record, timeout))

    @staticmethod
    def from_settings(phase: PhaseEnum,
                      pos_in_phase: Optional[PosInPhase],
                      environ: Optional[Dict[str, str]],
                      timeout: Optional[int] = None,
                      ) -> 'RecordingEntry':
        return RecordingEntry(StepInfo.of_settings(phase, pos_in_phase), environ, timeout)

    @staticmethod
    def from_environment(phase: PhaseEnum,
                         pos_in_phase: Optional[PosInPhase],
                         value: Optional[Dict[str, str]],
                         timeout: Optional[int] = None,
                         ) -> 'RecordingEntry':
        return RecordingEntry(StepInfo.of_environment(phase, pos_in_phase), value, timeout)
