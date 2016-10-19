from exactly_lib.execution import phases


class SimplePhaseStep(tuple):
    def __new__(cls,
                phase: phases.PhaseEnum,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phases.PhaseEnum:
        return self[0]

    @property
    def step(self) -> str:
        return self[1]


class PhaseStep(tuple):
    def __new__(cls,
                phase: phases.Phase,
                step: str):
        return tuple.__new__(cls, (phase, step))

    @property
    def phase(self) -> phases.Phase:
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


def _main_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'main')


def _validate_pre_eds_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-pre-eds')


def _validate_post_setup_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-post-setup')


CONFIGURATION__MAIN = _main_step(phases.CONFIGURATION)

SETUP__VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.SETUP)
SETUP__VALIDATE_POST_SETUP = _validate_post_setup_step(phases.SETUP)
SETUP__MAIN = _main_step(phases.SETUP)

ACT__VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.ACT)
ACT__VALIDATE_POST_SETUP = _validate_post_setup_step(phases.ACT)
ACT__MAIN = _main_step(phases.ACT)
ACT__PREPARE = PhaseStep(phases.ACT, 'script-prepare')
ACT__EXECUTE = PhaseStep(phases.ACT, 'script-execute')

BEFORE_ASSERT__VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.BEFORE_ASSERT)
BEFORE_ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phases.BEFORE_ASSERT)
BEFORE_ASSERT__MAIN = _main_step(phases.BEFORE_ASSERT)

ASSERT__VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.ASSERT)
ASSERT__VALIDATE_POST_SETUP = _validate_post_setup_step(phases.ASSERT)
ASSERT__MAIN = _main_step(phases.ASSERT)

CLEANUP__VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.CLEANUP)
CLEANUP__MAIN = _main_step(phases.CLEANUP)
