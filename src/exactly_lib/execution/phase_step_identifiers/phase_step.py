from exactly_lib.test_case import phase_identifier


class SimplePhaseStep(tuple):
    def __new__(cls,
                phase: phase_identifier.PhaseEnum,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phase_identifier.PhaseEnum:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]

    def __str__(self):
        return self[0].name + '/' + self[1]

    def __repr__(self):
        return str(self)


class PhaseStep(tuple):
    def __new__(cls,
                phase: phase_identifier.Phase,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phase_identifier.Phase:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]

    @property
    def simple(self) -> SimplePhaseStep:
        return SimplePhaseStep(self.phase.the_enum, self.step)

    def __str__(self):
        tail = '' if not self.step else '/' + self.step
        return self.phase.identifier + tail


def _main_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, 'main')


def _validate_pre_sds_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-pre-sds')


def _validate_post_setup_step(phase: phase_identifier.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-post-setup')


CONFIGURATION__MAIN = _main_step(phase_identifier.CONFIGURATION)

SETUP__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.SETUP)
SETUP__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.SETUP)
SETUP__MAIN = _main_step(phase_identifier.SETUP)

ACT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.ACT)
ACT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.ACT)
ACT__MAIN = _main_step(phase_identifier.ACT)
ACT__PREPARE = PhaseStep(phase_identifier.ACT, 'script-prepare')
ACT__EXECUTE = PhaseStep(phase_identifier.ACT, 'script-execute')

BEFORE_ASSERT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.BEFORE_ASSERT)
BEFORE_ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.BEFORE_ASSERT)
BEFORE_ASSERT__MAIN = _main_step(phase_identifier.BEFORE_ASSERT)

ASSERT__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.ASSERT)
ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phase_identifier.ASSERT)
ASSERT__MAIN = _main_step(phase_identifier.ASSERT)

CLEANUP__VALIDATE_PRE_SDS = _validate_pre_sds_step(phase_identifier.CLEANUP)
CLEANUP__MAIN = _main_step(phase_identifier.CLEANUP)
