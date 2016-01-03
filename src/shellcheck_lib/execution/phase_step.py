from shellcheck_lib.execution import phases


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

    def __str__(self):
        tail = '' if not self.step else '/' + self.step
        return self.phase.identifier + tail


def _main_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'main')


def _validate_pre_eds_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-pre-eds')


def _validate_post_eds_step(phase: phases.Phase) -> PhaseStep:
    return PhaseStep(phase, 'validate-post-eds')


ANONYMOUS_MAIN = _main_step(phases.ANONYMOUS)

SETUP_PRE_VALIDATE = _validate_pre_eds_step(phases.SETUP)
SETUP_POST_VALIDATE = _validate_post_eds_step(phases.SETUP)
SETUP_MAIN = _main_step(phases.SETUP)

ACT_VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.ACT)
ACT_VALIDATE_POST_EDS = _validate_post_eds_step(phases.ACT)
ACT_MAIN = _main_step(phases.ACT)
ACT_SCRIPT_VALIDATE = PhaseStep(phases.ACT, 'script-validation')
ACT_SCRIPT_EXECUTE = PhaseStep(phases.ACT, 'script-execute')

BEFORE_ASSERT_VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.BEFORE_ASSERT)
BEFORE_ASSERT_VALIDATE_POST_EDS = _validate_post_eds_step(phases.BEFORE_ASSERT)
BEFORE_ASSERT_MAIN = _main_step(phases.BEFORE_ASSERT)

ASSERT_VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.ASSERT)
ASSERT_VALIDATE_POST_EDS = _validate_post_eds_step(phases.ASSERT)
ASSERT_MAIN = _main_step(phases.ASSERT)

CLEANUP_VALIDATE_PRE_EDS = _validate_pre_eds_step(phases.CLEANUP)
CLEANUP_MAIN = _main_step(phases.CLEANUP)
